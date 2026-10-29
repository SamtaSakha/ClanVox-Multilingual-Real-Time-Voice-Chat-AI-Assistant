from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant|tool)$")
    content: str
    lang: Optional[str] = None
    created_at: Optional[datetime] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = None
    locale: Optional[str] = None
    mode: str = "chat"

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    language: str
    locale: str
    detected_code_switch: bool = False
    matrix_language: Optional[str] = None
    latency_ms: int = 0
