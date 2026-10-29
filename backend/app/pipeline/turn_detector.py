from typing import List

class SemanticTurnDetector:
    """Semantic Turn Detector: evaluates if a pause is mid-utterance thinking
    or a genuine end-of-turn to avoid cutting off users.
    """
    TRAILING_CONNECTORS = {
        "en": ["and", "or", "because", "so", "but", "like", "if", "um", "uh"],
        "hi": ["aur", "ya", "kyunki", "to", "lekin", "matlab", "agar"],
        "es": ["y", "o", "porque", "entonces", "pero", "este", "o sea"],
        "fr": ["et", "ou", "parce que", "alors", "mais", "euh"],
    }

    def is_complete_turn(self, partial_text: str, language: str = "en", silence_ms: int = 500) -> bool:
        trimmed = partial_text.strip()
        if not trimmed:
            return False

        # If user ends with terminal punctuation, high confidence of completion
        if trimmed[-1] in ".?!।。！？؟":
            return True

        words = trimmed.lower().split()
        if not words:
            return False

        last_word = words[-1]
        connectors = self.TRAILING_CONNECTORS.get(language, self.TRAILING_CONNECTORS["en"])

        # If ending with a connector or filler, user is likely hesitating / thinking
        if last_word in connectors:
            # Need a longer silence before cutting off
            return silence_ms > 1200

        # Normal speech turn completion after standard silence threshold
        return silence_ms >= 500
