from typing import Dict, List, Optional
from ..core.config import locales_registry

DIALECT_MARKERS: Dict[str, List[str]] = {
    "es-AR": ["che", "vos", "tenés", "podés", "posta", "quilombo", "laburo", "copado"],
    "es-MX": ["güey", "wey", "chido", "padre", "no manches", "¿mande?", "orale"],
    "ar-EG": ["إزيك", "باشا", "كده", "عايز", "أوي", "النهاردة", "تمام"],
    "hi-IN": ["jugaad", "scene", "bindaas", "faadu", "chalta hai", "yaar", "arre"],
    "en-IN": ["prep", "prepone", "revert back", "do the needful", "out of station", "passed out"]
}

class DialectIdentifier:
    def __init__(self, registry: Optional[Dict[str, Any]] = None):
        self.registry = registry or locales_registry

    def identify_locale(self, text: str, base_lang: str, default_locale: Optional[str] = None) -> str:
        lower = text.lower()
        best_locale = default_locale or f"{base_lang}-{base_lang.upper()}"
        highest_matches = 0

        for locale_code, markers in DIALECT_MARKERS.items():
            if locale_code.startswith(base_lang):
                matches = sum(1 for m in markers if m.lower() in lower)
                if matches > highest_matches:
                    highest_matches = matches
                    best_locale = locale_code

        return best_locale
