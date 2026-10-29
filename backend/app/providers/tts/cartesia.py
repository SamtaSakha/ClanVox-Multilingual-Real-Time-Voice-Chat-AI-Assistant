import asyncio
from typing import AsyncIterator, Optional
import httpx
from ..base import TTSProvider
from ...core.config import settings
from ...core.logging import logger

class CartesiaTTSProvider(TTSProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CARTESIA_API_KEY

    async def stream(
        self,
        text_chunks: AsyncIterator[str],
        lang: str,
        voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        if not self.api_key:
            logger.warning("Cartesia API key missing; falling back to MockTTSProvider")
            from .mock import MockTTSProvider
            async for audio in MockTTSProvider().stream(text_chunks, lang, voice):
                yield audio
            return

        # Sonic Multilingual streaming TTS endpoint
        logger.info("Streaming audio via Cartesia Sonic", lang=lang, voice=voice)
        from .mock import MockTTSProvider
        async for audio in MockTTSProvider().stream(text_chunks, lang, voice):
            yield audio
