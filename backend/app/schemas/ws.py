from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

# Client -> Server
class WSClientMessage(BaseModel):
    type: str # audio.chunk, text.message, config.update, interrupt
    data: Optional[str] = None # base64 audio
    text: Optional[str] = None
    language: Optional[str] = None
    voice: Optional[str] = None
    speed: Optional[float] = 1.0

# Server -> Client
class WSServerEvent(BaseModel):
    type: str # stt.partial, stt.final, llm.delta, tts.audio, state, tool.call, error
    text: Optional[str] = None
    lang: Optional[str] = None
    confidence: Optional[float] = None
    data: Optional[str] = None # base64 audio
    seq: Optional[int] = None
    value: Optional[str] = None # state: idle, listening, thinking, speaking, interrupted
    name: Optional[str] = None # tool name
    args: Optional[Dict[str, Any]] = None # tool args
    code: Optional[str] = None
    message: Optional[str] = None

