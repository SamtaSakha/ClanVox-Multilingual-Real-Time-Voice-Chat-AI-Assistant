import pytest
from backend.app.pipeline.orchestrator import TurnOrchestrator
from backend.app.memory.session_store import SessionMemory
from backend.app.providers.llm.mock import MockLLMProvider
from backend.app.providers.tts.mock import MockTTSProvider

def test_resolve_voice_default_female():
    mem = SessionMemory("test_voice_1", initial_lang="en", locale="en-US", voice_gender="female")
    orch = TurnOrchestrator(
        send_event=None,
        send_audio=None,
        memory=mem,
        llm=MockLLMProvider(),
        tts=MockTTSProvider()
    )

    # English Default Female
    voice_en_f = orch.resolve_voice(lang="en", locale="en-US", gender="female")
    name_en_f = orch.get_voice_name(lang="en", locale="en-US", gender="female")
    assert voice_en_f == "en-US-JennyNeural"
    assert name_en_f == "Aria"

    # Hindi Default Female
    voice_hi_f = orch.resolve_voice(lang="hi", locale="hi-IN", gender="female")
    name_hi_f = orch.get_voice_name(lang="hi", locale="hi-IN", gender="female")
    assert voice_hi_f == "hi-IN-SwaraNeural"
    assert name_hi_f == "Swara"

def test_resolve_voice_user_preferred_male():
    mem = SessionMemory("test_voice_2", initial_lang="en", locale="en-US", voice_gender="male")
    orch = TurnOrchestrator(
        send_event=None,
        send_audio=None,
        memory=mem,
        llm=MockLLMProvider(),
        tts=MockTTSProvider()
    )

    # English User-selected Male
    voice_en_m = orch.resolve_voice(lang="en", locale="en-US", gender="male")
    name_en_m = orch.get_voice_name(lang="en", locale="en-US", gender="male")
    assert voice_en_m == "en-US-GuyNeural"
    assert name_en_m == "Leo"

    # Hindi User-selected Male
    voice_hi_m = orch.resolve_voice(lang="hi", locale="hi-IN", gender="male")
    name_hi_m = orch.get_voice_name(lang="hi", locale="hi-IN", gender="male")
    assert voice_hi_m == "hi-IN-MadhurNeural"
    assert name_hi_m == "Aarav"

def test_session_create_default_gender():
    mem = SessionMemory("test_voice_3")
    assert mem.preferences.voice_gender == "female"

