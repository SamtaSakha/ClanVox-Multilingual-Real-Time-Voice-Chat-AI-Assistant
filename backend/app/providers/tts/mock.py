import asyncio
import math
import struct
from typing import AsyncIterator, Optional
from ..base import TTSProvider

class MockTTSProvider(TTSProvider):
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    async def stream(
        self,
        text_chunks: AsyncIterator[str],
        lang: str,
        voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        # Generate 16kHz 16-bit PCM audio frames per sentence/chunk
        frequency = 440.0 # 440 Hz tone
        frame_duration = 0.05 # 50 ms frame
        samples_per_frame = int(self.sample_rate * frame_duration)

        async for chunk in text_chunks:
            if not chunk.strip():
                continue
            # Output a short burst of audio representing the spoken words
            num_frames = max(2, min(len(chunk.split()) * 3, 10))
            for f in range(num_frames):
                frame_bytes = bytearray()
                for i in range(samples_per_frame):
                    t = float(f * samples_per_frame + i) / self.sample_rate
                    # Low volume sine wave
                    sample = int(0.15 * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
                    frame_bytes.extend(struct.pack("<h", sample))
                await asyncio.sleep(frame_duration)
                yield bytes(frame_bytes)
