import asyncio
from typing import AsyncIterator, Optional
from ..base import STTProvider, STTResult

class MockSTTProvider(STTProvider):
    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang

    async def stream(
        self,
        audio: AsyncIterator[bytes],
        lang_hint: Optional[str] = None
    ) -> AsyncIterator[STTResult]:
        total_bytes = 0
        async for chunk in audio:
            total_bytes += len(chunk)
            # Emit periodic partial results
            if total_bytes % 3200 == 0:
                yield STTResult(
                    text="Listening...",
                    is_final=False,
                    language=lang_hint or self.default_lang,
                    confidence=0.85
                )
            await asyncio.sleep(0.01)

        # On stream end, yield a mock final transcript if any audio was sent
        if total_bytes > 0:
            yield STTResult(
                text="Hello ClanVox, how are you?",
                is_final=True,
                language=lang_hint or self.default_lang,
                confidence=0.96
            )

