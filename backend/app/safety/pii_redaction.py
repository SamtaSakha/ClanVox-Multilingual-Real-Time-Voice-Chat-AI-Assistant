import re

PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

class PIIRedactor:
    """Masks Personally Identifiable Information (PII) before storage or logging."""

    def redact(self, text: str) -> str:
        redacted = EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
        redacted = CREDIT_CARD_REGEX.sub("[CARD_REDACTED]", redacted)
        redacted = PHONE_REGEX.sub("[PHONE_REDACTED]", redacted)
        return redacted

pii_redactor = PIIRedactor()
