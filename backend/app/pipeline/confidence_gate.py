from typing import Dict, Any

class ConfidenceGate:
    """Confidence Gate for Low-Resource and Tiered Languages (Gap 4).
    Prevents silent hallucination/errors by gracefully confirming or asking to repeat.
    """

    CONFIRMATION_TEMPLATES = {
        "en": "I heard: '{text}'. Is that correct?",
        "hi": "Maine suna: '{text}'. Kya yeh theek hai?",
        "es": "Escuché: '{text}'. ¿Es correcto?",
        "sw": "Nilisikia: '{text}'. Je, ni sawa?"
    }

    REPEAT_TEMPLATES = {
        "en": "I couldn't hear that clearly. Could you please repeat?",
        "hi": "Mujhe theek se sunai nahi diya. Kya aap dobara bol sakte hain?",
        "es": "No pude escucharte con claridad. ¿Podrías repetir, por favor?",
        "sw": "Sikukusikia vizuri. Tafadhali unaweza kurudia?"
    }

    def evaluate(self, stt_conf: float, lang_tier: int, lid_conf: float) -> str:
        if lang_tier <= 2 and stt_conf >= 0.80:
            return "proceed"
        if stt_conf >= 0.60:
            return "proceed_with_confirm"
        if stt_conf >= 0.40:
            return "ask_repeat"
        return "offer_alternative"

    def get_prompt_override(self, action: str, text: str, lang: str) -> str:
        if action == "proceed_with_confirm":
            tpl = self.CONFIRMATION_TEMPLATES.get(lang, self.CONFIRMATION_TEMPLATES["en"])
            return tpl.format(text=text)
        elif action == "ask_repeat":
            return self.REPEAT_TEMPLATES.get(lang, self.REPEAT_TEMPLATES["en"])
        elif action == "offer_alternative":
            return "I am having trouble processing the audio. You may type your message or switch to a supported dialect."
        return ""
