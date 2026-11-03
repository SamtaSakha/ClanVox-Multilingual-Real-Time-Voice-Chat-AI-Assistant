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
        # Distinct fundamental frequency and harmonics for female vs male
        is_male = False
        if voice:
            v_lower = voice.lower()
            if any(m in v_lower for m in ["male", "guy", "madhur", "alvaro", "henri", "conrad", "keita", "echo", "onyx", "leo"]):
                is_male = True

        fundamental = 210.0 if is_male else 480.0
        frame_duration = 0.05 # 50 ms frame
        samples_per_frame = int(self.sample_rate * frame_duration)

        async for chunk in text_chunks:
            clean = chunk.strip()
            if not clean:
                continue

            num_frames = max(2, min(len(clean.split()) * 3, 10))
            for f in range(num_frames):
                frame_bytes = bytearray()
                for i in range(samples_per_frame):
                    t = float(f * samples_per_frame + i) / self.sample_rate
                    # Rich harmonic blend with fundamental and 2nd harmonic
                    s1 = math.sin(2.0 * math.pi * fundamental * t)
                    s2 = 0.4 * math.sin(2.0 * math.pi * (fundamental * 2.0) * t)
                    sample = int(0.18 * 32767.0 * (s1 + s2))
                    frame_bytes.extend(struct.pack("<h", sample))
                await asyncio.sleep(frame_duration)
                yield bytes(frame_bytes)
