import base64
import math
import struct
from typing import List

def pcm16_to_base64(pcm_bytes: bytes) -> str:
    """Encode raw 16-bit PCM bytes to base64 string."""
    return base64.b64encode(pcm_bytes).decode("ascii")

def base64_to_pcm16(b64_str: str) -> bytes:
    """Decode base64 string back to raw 16-bit PCM bytes."""
    return base64.b64decode(b64_str)

def calculate_rms(pcm_bytes: bytes) -> float:
    """Compute Root Mean Square (RMS) energy of 16-bit mono PCM."""
    if len(pcm_bytes) < 2:
        return 0.0
    num_samples = len(pcm_bytes) // 2
    samples = struct.unpack(f"<{num_samples}h", pcm_bytes[:num_samples * 2])
    sum_squares = sum(float(s * s) for s in samples)
    return math.sqrt(sum_squares / num_samples)

def generate_silence(duration_sec: float, sample_rate: int = 16000) -> bytes:
    """Generate silent PCM frames."""
    num_samples = int(duration_sec * sample_rate)
    return b"\x00" * (num_samples * 2)
