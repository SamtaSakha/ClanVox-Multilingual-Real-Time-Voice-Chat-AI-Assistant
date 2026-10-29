from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Any

@dataclass
class STTResult:
    text: str
    is_final: bool
    language: Optional[str]
    confidence: float

class STTProvider(ABC):
    @abstractmethod
    async def stream(
        self,
        audio: AsyncIterator[bytes],
        lang_hint: Optional[str] = None
    ) -> AsyncIterator[STTResult]:
        """Stream raw audio frames and yield interim and final STT results."""
        ...

class LLMProvider(ABC):
    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream responses from LLM yielding text deltas or tool calls.
        Format: {'type': 'text', 'text': '...'} or {'type': 'tool_call', 'name': '...', 'args': {...}}
        """
        ...

class TTSProvider(ABC):
    @abstractmethod
    async def stream(
        self,
        text_chunks: AsyncIterator[str],
        lang: str,
        voice: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """Stream audio bytes corresponding to input text chunks."""
        ...
