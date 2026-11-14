import re
from typing import AsyncIterator, List

TERMINAL_PUNCTUATION = set(".!?।。！？؟…\n")
EARLY_BREAK_PUNCTUATION = set(",;:—–،")
ABBREVIATIONS = {"dr.", "mr.", "mrs.", "ms.", "e.g.", "i.e.", "etc.", "vs.", "prof."}

def is_abbreviation_or_decimal(text: str, idx: int) -> bool:
    """Check if the dot at idx is part of an abbreviation (e.g. 'Dr.') or decimal ('3.14')."""
    # Check decimal
    if idx > 0 and idx < len(text) - 1:
        if text[idx - 1].isdigit() and text[idx + 1].isdigit():
            return True

    # Check abbreviation
    start = max(0, idx - 4)
    window = text[start:idx + 1].lower()
    for ab in ABBREVIATIONS:
        if window.endswith(ab):
            return True
    return False

async def chunk_sentences(
    text_stream: AsyncIterator[str],
    lang: str = "en",
    first_chunk_min_chars: int = 15
) -> AsyncIterator[str]:
    """Streams sentences as soon as they form, optimizing time-to-first-audio (TTFA).
    Supports English, Hindi (purna viram '।'), CJK ('。'), Arabic ('؟'), etc.
    """
    buffer = ""
    is_first_chunk = True

    async for token in text_stream:
        buffer += token

        # Early comma/punctuation split for the first chunk to minimize initial latency
        if is_first_chunk and len(buffer) >= first_chunk_min_chars:
            for idx, ch in enumerate(buffer):
                if ch in EARLY_BREAK_PUNCTUATION and idx >= first_chunk_min_chars:
                    chunk = buffer[:idx + 1].strip()
                    buffer = buffer[idx + 1:].lstrip()
                    if chunk:
                        is_first_chunk = False
                        yield chunk
                    break

        # Check for sentence terminators
        i = 0
        while i < len(buffer):
            ch = buffer[i]
            if ch in TERMINAL_PUNCTUATION:
                if ch == "." and is_abbreviation_or_decimal(buffer, i):
                    i += 1
                    continue

                chunk = buffer[:i + 1].strip()
                buffer = buffer[i + 1:].lstrip()
                if chunk:
                    is_first_chunk = False
                    yield chunk
                i = 0
                continue
            i += 1

    remaining = buffer.strip()
    if remaining:
        yield remaining

