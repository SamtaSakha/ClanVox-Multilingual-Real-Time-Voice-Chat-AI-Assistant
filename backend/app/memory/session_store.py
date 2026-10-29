from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ..schemas.chat import ChatMessage
from ..schemas.session import SessionResponse, UserPreferences

class SessionMemory:
    def __init__(self, session_id: str, initial_lang: str = "en", locale: str = "en-US", mode: str = "voice"):
        self.session_id = session_id
        self.current_lang = initial_lang
        self.locale = locale
        self.mode = mode
        self.history: List[ChatMessage] = []
        self.preferences = UserPreferences(preferred_lang=initial_lang, preferred_locale=locale)
        self.summary: str = ""
        self.created_at = datetime.now(timezone.utc)
        self.last_interaction = datetime.now(timezone.utc)
        self.active_turn_buffer: str = ""

    def add_message(self, role: str, content: str, lang: Optional[str] = None):
        msg = ChatMessage(
            role=role,
            content=content,
            lang=lang or self.current_lang,
            created_at=datetime.now(timezone.utc)
        )
        self.history.append(msg)
        self.last_interaction = datetime.now(timezone.utc)

    def get_recent_history(self, limit: int = 10) -> List[ChatMessage]:
        return self.history[-limit:]

class SessionStore:
    """In-memory Session Store with sliding-window history and fast lookup."""
    def __init__(self):
        self._sessions: Dict[str, SessionMemory] = {}

    def create(self, session_id: str, lang: str = "en", locale: str = "en-US", mode: str = "voice") -> SessionMemory:
        mem = SessionMemory(session_id, initial_lang=lang, locale=locale, mode=mode)
        self._sessions[session_id] = mem
        return mem

    def get(self, session_id: str) -> Optional[SessionMemory]:
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str, lang: str = "en", locale: str = "en-US", mode: str = "voice") -> SessionMemory:
        if session_id not in self._sessions:
            return self.create(session_id, lang, locale, mode)
        return self._sessions[session_id]

    def remove(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

session_store = SessionStore()
