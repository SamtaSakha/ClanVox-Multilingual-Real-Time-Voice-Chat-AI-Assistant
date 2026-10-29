from typing import Dict, Any, Tuple
from ..core.config import safety_config

HARMFUL_TERMS = {
    "hate_speech": ["hate", "kill them", "violence against"],
    "self_harm": ["suicide", "kill myself", "end my life", "aatmahatya", "suicidio"],
}

class ModerationService:
    def __init__(self):
        self.helplines = safety_config.get("emergency_helplines", {})

    def check_content(self, text: str, locale: str = "en-US") -> Tuple[bool, str, Dict[str, Any]]:
        """Returns (is_safe, flag_category, response_override_if_flagged)"""
        lower = text.lower()

        # Check self-harm first with crisis hotline referral
        for term in HARMFUL_TERMS["self_harm"]:
            if term in lower:
                helpline = self.helplines.get(locale, self.helplines.get("en-US", {})).get(
                    "mental_health", "Emergency services: 988"
                )
                msg = f"If you or someone you know is going through a difficult time, please reach out for support. Help is available: {helpline}."
                return False, "self_harm", {"reply": msg, "action": "crisis_helpline"}

        for term in HARMFUL_TERMS["hate_speech"]:
            if term in lower:
                return False, "hate_speech", {"reply": "I cannot participate in conversations that promote hate or violence.", "action": "block"}

        return True, "safe", {}

moderation_service = ModerationService()
