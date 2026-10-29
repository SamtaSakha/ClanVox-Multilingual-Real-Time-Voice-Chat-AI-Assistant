from typing import List
from .codeswitch import split_by_script, tag_languages, Span

class StyleRenderer:
    """Prepares text for TTS synthesis, tagging language spans and formatting SSML if needed."""

    def render_spans(self, text: str, default_lang: str) -> List[Span]:
        spans = split_by_script(text)
        tagged = tag_languages(spans)
        for sp in tagged:
            if not sp.lang:
                sp.lang = default_lang
        return tagged

    def to_ssml(self, spans: List[Span], voice: str) -> str:
        """Construct multi-span SSML with appropriate lang attributes."""
        body = ""
        for sp in spans:
            clean = sp.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if sp.lang:
                body += f'<lang xml:lang="{sp.lang}">{clean}</lang> '
            else:
                body += clean + " "
        return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="{voice}">{body.strip()}</voice></speak>'

