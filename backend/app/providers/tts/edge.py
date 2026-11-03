import asyncio
from typing import AsyncIterator, Optional
from ..base import TTSProvider
from ...core.logging import logger

class EdgeTTSProvider(TTSProvider):
    """Realistic Neural TTS using edge-tts. Supports high-fidelity female and male voices
    across 100+ languages without requiring any paid API key.
    """
    def __init__(self, default_voice: str = "en-US-JennyNeural"):
        self.default_voice = default_voice

    async def stream(
        self,
        text_chunks: AsyncIterator[str],
        lang: str,
        voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        try:
            import edge_tts
        except ImportError:
            logger.warning("edge-tts not installed; falling back to MockTTSProvider")
            from .mock import MockTTSProvider
            async for chunk in MockTTSProvider().stream(text_chunks, lang, voice):
                yield chunk
            return

        target_voice = voice or self.default_voice
        logger.info("Synthesizing realistic audio via EdgeTTS", lang=lang, voice=target_voice)

        async for chunk_text in text_chunks:
            clean_text = chunk_text.strip()
            if not clean_text:
                continue

            try:
                communicator = edge_tts.Communicate(clean_text, target_voice)
                async for chunk in communicator.stream():
                    if chunk["type"] == "audio" and chunk["data"]:
                        yield chunk["data"]
            except Exception as e:
                logger.error("EdgeTTS generation error", error=str(e), voice=target_voice)
                # Fallback to harmonic audio on error
                from .mock import MockTTSProvider
                async def fallback_stream():
                    yield clean_text
                async for audio_bytes in MockTTSProvider().stream(fallback_stream(), lang, voice=target_voice):
                    yield audio_bytes

