import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.config import CONFIG_DIR, locales_registry

FORMALITY_RULES = {
    "ja": {"formal": "teineigo/keigo (です・ます, 敬語)", "casual": "plain form (だ/る)"},
    "ko": {"formal": "합쇼체/해요체", "casual": "반말"},
    "hi": {"formal": "आप + respectful verbs", "casual": "तुम / तू"},
    "es": {"formal": "usted", "casual": "tú / vos (by locale)"},
    "de": {"formal": "Sie", "casual": "du"},
    "fr": {"formal": "vous", "casual": "tu"},
}

class ContextEngine:
    def __init__(self):
        self.culture_dir = CONFIG_DIR / "culture"

    def decide_formality(self, user_preference: Optional[str], locale: str, user_text: str) -> str:
        if user_preference and user_preference != "auto":
            return user_preference

        base_lang = locale.split("-")[0]
        lower = user_text.lower()

        # Mirror user's own register
        if base_lang == "hi":
            if "tu " in lower or "tum " in lower:
                return "casual"
            return "formal" # Default to respectful आप

        if base_lang == "es":
            if "usted" in lower:
                return "formal"
            return "casual"

        locale_cfg = locales_registry.get(locale, {})
        return locale_cfg.get("default_formality", "neutral_polite")

    def retrieve_slang_lexicon(self, locale: str, query: str) -> List[Dict[str, str]]:
        lexicon_file = self.culture_dir / locale / "slang.jsonl"
        results = []
        if lexicon_file.exists():
            with open(lexicon_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get("term", "").lower() in query.lower() or not query:
                            results.append(entry)
        return results[:3]

    def retrieve_exemplars(self, locale: str) -> List[Dict[str, str]]:
        exemplars_file = self.culture_dir / locale / "exemplars.jsonl"
        results = []
        if exemplars_file.exists():
            with open(exemplars_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
        return results[:2]
