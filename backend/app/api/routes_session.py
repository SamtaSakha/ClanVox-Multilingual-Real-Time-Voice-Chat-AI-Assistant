import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from ..core.config import languages_registry, locales_registry, settings
from ..memory.session_store import session_store
from ..schemas.session import SessionCreate, SessionResponse, UserPreferences

router = APIRouter(prefix="/v1", tags=["sessions"])

@router.post("/sessions", response_model=SessionResponse)
async def create_session(req: SessionCreate):
    session_id = str(uuid.uuid4())
    lang = req.initial_language or settings.DEFAULT_LANGUAGE
    locale = req.locale or settings.DEFAULT_LOCALE
    mem = session_store.create(session_id, lang=lang, locale=locale, mode=req.mode)

    # Optional LiveKit token creation
    livekit_token = f"dev-token-{session_id}"
    return SessionResponse(
        session_id=session_id,
        user_id=req.user_id or "guest",
        mode=req.mode,
        language=lang,
        locale=locale,
        livekit_token=livekit_token,
        livekit_url=settings.LIVEKIT_URL,
        created_at=mem.created_at
    )

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    mem = session_store.get(session_id)
    if not mem:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": mem.session_id,
        "language": mem.current_lang,
        "locale": mem.locale,
        "mode": mem.mode,
        "history": [msg.model_dump() for msg in mem.history],
        "created_at": mem.created_at,
        "summary": mem.summary
    }

@router.get("/languages")
async def list_languages():
    return {
        "languages": languages_registry,
        "locales": locales_registry
    }

@router.patch("/users/me/preferences")
async def update_preferences(prefs: UserPreferences):
    return {"status": "updated", "preferences": prefs}
