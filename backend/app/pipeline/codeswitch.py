import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

SCRIPT_KEYS = (
    "DEVANAGARI", "ARABIC", "LATIN", "CJK", "HIRAGANA", "KATAKANA",
    "HANGUL", "THAI", "TAMIL", "BENGALI", "GUJARATI", "TELUGU",
    "KANNADA", "MALAYALAM", "CYRILLIC", "GREEK", "HEBREW"
)

SCRIPT_TO_LANG: Dict[str, str] = {
    "DEVANAGARI": "hi",
    "ARABIC": "ar",
    "TAMIL": "ta",
    "TELUGU": "te",
    "BENGALI": "bn",
    "GUJARATI": "gu",
    "CJK": "zh",
    "HIRAGANA": "ja",
    "KATAKANA": "ja",
    "HANGUL": "ko",
    "THAI": "th",
    "CYRILLIC": "ru",
    "GREEK": "el",
    "HEBREW": "he",
}

# Common Hinglish markers written in Roman/Latin script
HINGLISH_WORDS: Set[str] = {
    "kya", "hai", "hain", "hoon", "nahi", "nahin", "acha", "achha", "bhai",
    "karo", "karenge", "batao", "kaise", "kaisa", "kaisi", "mera", "meri",
    "mere", "aap", "tum", "hum", "yeh", "woh", "kab", "kahan", "kyun",
    "chahiye", "hoga", "hogi", "theek", "shukriya", "dhanyawad", "lekin"
}

# Common Spanglish markers
SPANGLISH_WORDS: Set[str] = {
    "hola", "amigo", "amiga", "gracias", "por", "favor", "bueno", "pero",
    "como", "estas", "todo", "bien", "vamos", "ahora", "claro", "que"
}

def script_of(ch: str) -> str:
    """Identify the Unicode script category of a character."""
    if ch.isspace() or ch.isdigit() or not ch.isalpha():
        return "COMMON"
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return "COMMON"
    return next((s for s in SCRIPT_KEYS if s in name), "OTHER")

@dataclass
class Span:
    text: str
    script: str
    lang: Optional[str] = None

def split_by_script(text: str) -> List[Span]:
    """Splits a string into consecutive spans of uniform Unicode scripts."""
    spans: List[Span] = []
    buf, cur = "", None
    for ch in text:
        s = script_of(ch)
        if s == "COMMON":
            buf += ch
            continue
        if cur is None or s == cur:
            cur = s
            buf += ch
        else:
            spans.append(Span(text=buf, script=cur))
            buf, cur = ch, s
    if buf:
        spans.append(Span(text=buf, script=cur or "COMMON"))
    return spans

def tag_languages(spans: List[Span], candidate_langs: Optional[List[str]] = None) -> List[Span]:
    """Tag each span with a language code.
    If script is LATIN, examines vocabulary to distinguish English from Romanized Hindi (Hinglish) or Spanish.
    """
    for sp in spans:
        if sp.script in SCRIPT_TO_LANG:
            sp.lang = SCRIPT_TO_LANG[sp.script]
        elif sp.script == "LATIN":
            words = set(w.lower() for w in sp.text.split())
            if words & HINGLISH_WORDS:
                sp.lang = "hi" # Roman Hindi / Hinglish
            elif words & SPANGLISH_WORDS:
                sp.lang = "es"
            else:
                sp.lang = "en"
        else:
            sp.lang = "en"
    return spans

def matrix_language(spans: List[Span]) -> str:
    """Determine the matrix (base frame) language based on word count per language."""
    counts: Dict[str, int] = {}
    for sp in spans:
        lang = sp.lang or "en"
        words_count = len(sp.text.split())
        counts[lang] = counts.get(lang, 0) + words_count

    if not counts:
        return "en"
    return max(counts, key=counts.get)

def is_code_switched(spans: List[Span]) -> bool:
    """Check if utterance contains words from more than one distinct language."""
    langs = {sp.lang for sp in spans if sp.lang and sp.lang != "COMMON"}
    return len(langs) > 1

