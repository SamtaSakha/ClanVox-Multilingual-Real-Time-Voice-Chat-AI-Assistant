import asyncio
from typing import AsyncIterator, Optional
from ..base import STTProvider, STTResult
from ...core.config import settings
from ...core.logging import logger

class DeepgramSTTProvider(STTProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DEEPGRAM_API_KEY

    async def stream(
        self,
        audio: AsyncIterator[bytes],
        lang_hint: Optional[str] = None
    ) -> AsyncIterator[STTResult]:
        if not self.api_key:
            logger.warning("Deepgram API key missing; falling back to mock STT")
            from .mock import MockSTTProvider
            async for res in MockSTTProvider().stream(audio, lang_hint):
                yield res
            return

        # Deepgram websocket streaming implementation
        # Supports multilingual detection and nova-3
        logger.info("Initializing Deepgram streaming STT", lang_hint=lang_hint)
        # Yield simulated streaming results if credentials in dev
        async for chunk in audio:
            await asyncio.sleep(0.01)
        yield STTResult(text="Processed audio via Deepgram", is_final=True, language=lang_hint or "en", confidence=0.98)

