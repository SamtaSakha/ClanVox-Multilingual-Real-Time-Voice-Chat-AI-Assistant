from .audio_utils import calculate_rms

class VoiceActivityDetector:
    """Voice Activity Detector tracking speech vs silence with configurable energy threshold."""
    def __init__(self, energy_threshold: float = 350.0, min_speech_frames: int = 3, min_silence_frames: int = 10):
        self.energy_threshold = energy_threshold
        self.min_speech_frames = min_speech_frames
        self.min_silence_frames = min_silence_frames
        self.speech_frames = 0
        self.silence_frames = 0
        self.is_speaking = False

    def process_frame(self, pcm_bytes: bytes) -> bool:
        """Process a PCM audio frame and return True if currently in active speech."""
        rms = calculate_rms(pcm_bytes)
        if rms >= self.energy_threshold:
            self.speech_frames += 1
            self.silence_frames = 0
            if self.speech_frames >= self.min_speech_frames:
                self.is_speaking = True
        else:
            self.silence_frames += 1
            if self.silence_frames >= self.min_silence_frames:
                self.speech_frames = 0
                self.is_speaking = False
        return self.is_speaking

    def reset(self):
        self.speech_frames = 0
        self.silence_frames = 0
        self.is_speaking = False

