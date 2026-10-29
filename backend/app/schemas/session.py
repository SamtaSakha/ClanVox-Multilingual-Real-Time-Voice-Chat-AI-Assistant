from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SessionCreate(BaseModel):
    user_id: Optional[str] = "guest"
    mode: str = Field(default="voice", pattern="^(voice|chat|interpreter)$")
    initial_language: Optional[str] = "en"
    locale: Optional[str] = "en-US"

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    mode: str
    language: str
    locale: str
    livekit_token: Optional[str] = None
    livekit_url: Optional[str] = None
    created_at: datetime

class UserPreferences(BaseModel):
    preferred_lang: str = "en"
    preferred_locale: str = "en-US"
    voice_id: str = "en-US-JennyNeural"
    speech_rate: float = 1.0
    consent_recording: bool = False
    formality: str = "auto"
