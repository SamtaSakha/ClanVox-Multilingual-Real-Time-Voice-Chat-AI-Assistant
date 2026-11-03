import asyncio
from typing import AsyncIterator, Optional
from ..base import TTSProvider
from ...core.config import settings
from ...core.logging import logger

class OpenAITTSProvider(TTSProvider):
    """Realistic speech generation using OpenAI TTS API (tts-1)."""
    def __init__(self, api_key: Optional[str] = None, model: str = "tts-1"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model

    async def stream(
        self,
        text_chunks: AsyncIterator[str],
        lang: str,
        voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        if not self.api_key:
            logger.warning("OpenAI API key missing; falling back to EdgeTTSProvider")
            from .edge import EdgeTTSProvider
            async for chunk in EdgeTTSProvider().stream(text_chunks, lang, voice):
                yield chunk
            return

        import openai
        client = openai.AsyncOpenAI(api_key=self.api_key)

        # Map voice to OpenAI voice name if needed
        voice_map = {
            "female": "nova",
            "male": "echo",
            "aria": "nova",
            "leo": "echo",
        }
        openai_voice = voice_map.get(voice.lower(), "nova") if voice else "nova"
        if voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
            openai_voice = voice

        logger.info("Streaming realistic speech via OpenAI TTS", voice=openai_voice)

        async for chunk_text in text_chunks:
            clean_text = chunk_text.strip()
            if not clean_text:
                continue

            try:
                response = await client.audio.speech.create(
                    model=self.model,
                    voice=openai_voice,
                    input=clean_text,
                    response_format="mp3"
                )
                yield response.content
            except Exception as e:
                logger.error("OpenAI TTS generation failed", error=str(e))
                from .edge import EdgeTTSProvider
                async def fallback():
                    yield clean_text
                async for chunk in EdgeTTSProvider().stream(fallback(), lang, voice):
                    yield chunk
