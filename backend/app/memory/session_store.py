from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ..core.history_logger import history_logger
from ..schemas.chat import ChatMessage
from ..schemas.session import SessionResponse, UserPreferences

class SessionMemory:
    def __init__(self, session_id: str, initial_lang: str = "en", locale: str = "en-US", mode: str = "voice", voice_gender: str = "female"):
        self.session_id = session_id
        self.current_lang = initial_lang
        self.locale = locale
        self.mode = mode
        self.history: List[ChatMessage] = []
        self.preferences = UserPreferences(preferred_lang=initial_lang, preferred_locale=locale, voice_gender=voice_gender)
        self.summary: str = ""
        self.created_at = datetime.now(timezone.utc)
        self.last_interaction = datetime.now(timezone.utc)
        self.active_turn_buffer: str = ""

    def add_message(self, role: str, content: str, lang: Optional[str] = None):
        msg_lang = lang or self.current_lang
        msg = ChatMessage(
            role=role,
            content=content,
            lang=msg_lang,
            created_at=datetime.now(timezone.utc)
        )
        self.history.append(msg)
        self.last_interaction = datetime.now(timezone.utc)

        # Log activity and save transcript to history folder
        try:
            history_logger.log_message(self.session_id, role, content, msg_lang)
            history_logger.save_session_snapshot(self.session_id, {
                "session_id": self.session_id,
                "language": self.current_lang,
                "locale": self.locale,
                "mode": self.mode,
                "voice_gender": self.preferences.voice_gender,
                "created_at": self.created_at.isoformat(),
                "history": [
                    {
                        "role": m.role,
                        "content": m.content,
                        "lang": m.lang,
                        "created_at": m.created_at.isoformat() if hasattr(m.created_at, "isoformat") else str(m.created_at)
                    }
                    for m in self.history
                ]
            })
        except Exception:
            pass

    def get_recent_history(self, limit: int = 10) -> List[ChatMessage]:
        return self.history[-limit:]

class SessionStore:
    """In-memory Session Store with sliding-window history, fast lookup, and history folder persistence."""
    def __init__(self):
        self._sessions: Dict[str, SessionMemory] = {}

    def create(self, session_id: str, lang: str = "en", locale: str = "en-US", mode: str = "voice", voice_gender: str = "female") -> SessionMemory:
        mem = SessionMemory(session_id, initial_lang=lang, locale=locale, mode=mode, voice_gender=voice_gender)
        self._sessions[session_id] = mem
        try:
            history_logger.log_activity("session.created", session_id, {
                "language": lang,
                "locale": locale,
                "mode": mode,
                "voice_gender": voice_gender
            })
        except Exception:
            pass
        return mem

    def get(self, session_id: str) -> Optional[SessionMemory]:
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str, lang: str = "en", locale: str = "en-US", mode: str = "voice", voice_gender: str = "female") -> SessionMemory:
        if session_id not in self._sessions:
            return self.create(session_id, lang, locale, mode, voice_gender=voice_gender)
        return self._sessions[session_id]

    def remove(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

session_store = SessionStore()
