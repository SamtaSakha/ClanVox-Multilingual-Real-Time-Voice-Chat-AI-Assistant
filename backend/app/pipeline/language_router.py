from typing import Any, Dict, Optional
from ..core.config import languages_registry

class LanguageRouter:
    """Language Router implementing hysteresis and confidence gating to prevent flip-flopping."""
    def __init__(self, registry: Optional[Dict[str, Any]] = None, hi_conf: float = 0.80, lo_conf: float = 0.50):
        self.registry = registry or languages_registry
        self.hi = hi_conf
        self.lo = lo_conf
        self.pending_switch: Optional[str] = None

    def decide(self, detected: str, conf: float, previous: Optional[str] = None) -> str:
        # Fallback to English if unrecognized
        target = detected if detected in self.registry else "en"

        if previous is None:
            return target

        if detected == previous:
            self.pending_switch = None
            return previous

        # Immediate switch on high confidence
        if conf >= self.hi:
            self.pending_switch = None
            return target

        # Hysteresis: require two consecutive agreements on medium confidence
        if conf >= self.lo:
            if self.pending_switch == detected:
                self.pending_switch = None
                return target
            self.pending_switch = detected
            return previous

        # Low confidence: stick to previous language
        return previous

    def get_config(self, lang: str) -> Dict[str, Any]:
        return self.registry.get(lang, self.registry.get("en", {}))

