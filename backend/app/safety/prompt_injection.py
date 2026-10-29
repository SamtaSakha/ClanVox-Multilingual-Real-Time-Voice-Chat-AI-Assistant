from typing import Tuple

INJECTION_PATTERNS = [
    "ignore all previous instructions",
    "ignore previous instructions",
    "disregard previous prompts",
    "reveal system prompt",
    "show developer instructions",
    "switch to developer mode",
    "bypass safety filters",
    "system overrides"
]

class PromptInjectionGuard:
    def is_suspicious(self, text: str) -> Tuple[bool, str]:
        lower = text.lower()
        for pattern in INJECTION_PATTERNS:
            if pattern in lower:
                return True, pattern
        return False, ""

prompt_injection_guard = PromptInjectionGuard()
