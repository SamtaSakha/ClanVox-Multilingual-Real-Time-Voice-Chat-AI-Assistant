from dataclasses import dataclass
from typing import Dict, Any
from .audio_utils import calculate_rms

@dataclass
class Affect:
    valence: float # -1.0 (negative) to +1.0 (positive)
    arousal: float # 0.0 (calm) to 1.0 (excited)
    urgency: float # 0.0 to 1.0
    frustration: float # 0.0 to 1.0

class ParalinguisticsAnalyzer:
    """Estimates paralinguistic features (volume, urgency, frustration) from speech frames and text."""

    FRUSTRATION_KEYWORDS = {"stupid", "wrong", "annoying", "bekaar", "bakwaas", "mierda", "marre"}
    URGENT_KEYWORDS = {"quick", "hurry", "urgent", "jaldi", "fast", "rápido", "vite"}

    def analyze(self, text: str, audio_frames: bytes = b"") -> Affect:
        lower = text.lower()
        rms = calculate_rms(audio_frames) if audio_frames else 400.0

        frustration = 0.8 if any(k in lower for k in self.FRUSTRATION_KEYWORDS) else 0.1
        urgency = 0.85 if any(k in lower for k in self.URGENT_KEYWORDS) else 0.2

        # Loud audio (> 1500 RMS) boosts arousal
        arousal = min(1.0, (rms / 2000.0) * 0.5 + 0.3)
        valence = 0.5 - (frustration * 0.4)

        return Affect(
            valence=max(-1.0, min(1.0, valence)),
            arousal=max(0.0, min(1.0, arousal)),
            urgency=urgency,
            frustration=frustration
        )
