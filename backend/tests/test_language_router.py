import pytest
from backend.app.pipeline.language_router import LanguageRouter

def test_router_high_confidence():
    router = LanguageRouter({"en": {}, "hi": {}, "es": {}}, hi_conf=0.80, lo_conf=0.50)
    # First turn
    lang = router.decide(detected="hi", conf=0.85, previous=None)
    assert lang == "hi"

    # Immediate switch on high confidence
    lang2 = router.decide(detected="es", conf=0.90, previous="hi")
    assert lang2 == "es"

def test_router_hysteresis_low_confidence():
    router = LanguageRouter({"en": {}, "hi": {}, "es": {}}, hi_conf=0.80, lo_conf=0.50)
    # Sticking to previous on medium confidence until repeated
    lang1 = router.decide(detected="hi", conf=0.60, previous="en")
    assert lang1 == "en" # Needs second confirmation

    # Second turn agrees
    lang2 = router.decide(detected="hi", conf=0.60, previous="en")
    assert lang2 == "hi"
