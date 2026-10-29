import asyncio
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.config import settings
from ..core.logging import logger
from ..memory.session_store import session_store
from ..pipeline.audio_utils import base64_to_pcm16, pcm16_to_base64
from ..pipeline.orchestrator import TurnOrchestrator
from ..pipeline.vad import VoiceActivityDetector
from ..pipeline.turn_detector import SemanticTurnDetector
from ..providers.llm.mock import MockLLMProvider
from ..providers.llm.openai import OpenAILLMProvider
from ..providers.stt.mock import MockSTTProvider
from ..providers.stt.deepgram import DeepgramSTTProvider
from ..providers.tts.mock import MockTTSProvider
from ..providers.tts.cartesia import CartesiaTTSProvider

router = APIRouter(tags=["realtime"])

def create_providers():
    # Factory selecting providers according to config / settings
    stt = DeepgramSTTProvider() if settings.STT_PROVIDER == "deepgram" else MockSTTProvider()
    llm = OpenAILLMProvider() if settings.LLM_PROVIDER == "openai" else MockLLMProvider()
    tts = CartesiaTTSProvider() if settings.TTS_PROVIDER == "cartesia" else MockTTSProvider()
    return stt, llm, tts

@router.websocket("/v1/realtime")
async def websocket_realtime_endpoint(websocket: WebSocket, session_id: Optional[str] = None):
    await websocket.accept()
    sess_id = session_id or "default_session"
    mem = session_store.get_or_create(sess_id, lang=settings.DEFAULT_LANGUAGE, locale=settings.DEFAULT_LOCALE, mode="voice")

    stt_provider, llm_provider, tts_provider = create_providers()
    vad = VoiceActivityDetector()
    semantic_turn = SemanticTurnDetector()

    seq_counter = 0

    async def send_event(data: dict):
        try:
            await websocket.send_text(json.dumps(data))
        except Exception:
            pass

    async def send_audio(pcm_bytes: bytes):
        nonlocal seq_counter
        seq_counter += 1
        b64 = pcm16_to_base64(pcm_bytes)
        await send_event({"type": "tts.audio", "data": b64, "seq": seq_counter})

    orchestrator = TurnOrchestrator(
        send_event=send_event,
        send_audio=send_audio,
        memory=mem,
        llm=llm_provider,
        tts=tts_provider,
    )

    await orchestrator.update_state("idle")
    logger.info("Realtime WebSocket client connected", session_id=sess_id)

    audio_queue: asyncio.Queue[bytes] = asyncio.Queue()

    async def stt_worker():
        """Consumes PCM audio chunks from queue and passes them to the STT provider."""
        async def audio_stream_generator():
            while True:
                chunk = await audio_queue.get()
                if chunk is None:
                    break
                yield chunk

        try:
            async for result in stt_provider.stream(audio_stream_generator(), lang_hint=mem.current_lang):
                if result.is_final:
                    await send_event({
                        "type": "stt.final",
                        "text": result.text,
                        "lang": result.language or mem.current_lang,
                        "confidence": result.confidence
                    })
                    await orchestrator.on_user_final(
                        text=result.text,
                        detected_lang=result.language or mem.current_lang,
                        conf=result.confidence
                    )
                else:
                    await send_event({
                        "type": "stt.partial",
                        "text": result.text,
                        "lang": result.language or mem.current_lang
                    })
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("STT worker error", error=str(e))

    stt_task = asyncio.create_task(stt_worker())

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            msg_type = data.get("type")

            if msg_type == "audio.chunk":
                b64_audio = data.get("data", "")
                if b64_audio:
                    pcm_bytes = base64_to_pcm16(b64_audio)
                    is_user_speaking = vad.process_frame(pcm_bytes)

                    # Barge-in: if user starts speaking while assistant is speaking, interrupt!
                    if is_user_speaking and orchestrator.state == "speaking":
                        logger.info("User barge-in detected! Interrupting assistant playback.")
                        await orchestrator.on_barge_in()

                    await audio_queue.put(pcm_bytes)

            elif msg_type == "text.message":
                text = data.get("text", "")
                lang = data.get("language") or mem.current_lang
                logger.info("Received real-time text message", text=text, lang=lang)
                await send_event({"type": "stt.final", "text": text, "lang": lang, "confidence": 1.0})
                await orchestrator.on_user_final(text=text, detected_lang=lang, conf=1.0)

            elif msg_type == "config.update":
                if "language" in data:
                    mem.current_lang = data["language"]
                if "voice" in data:
                    mem.preferences.voice_id = data["voice"]
                if "speed" in data:
                    mem.preferences.speech_rate = float(data["speed"])
                logger.info("Updated real-time session config", lang=mem.current_lang, voice=mem.preferences.voice_id)

            elif msg_type == "interrupt":
                logger.info("Manual interrupt received from client")
                await orchestrator.on_barge_in()

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", session_id=sess_id)
    except Exception as e:
        logger.error("WebSocket exception", session_id=sess_id, error=str(e))
    finally:
        await orchestrator.cancel_reply()
        await audio_queue.put(None)
        stt_task.cancel()

