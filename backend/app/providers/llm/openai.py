from typing import Any, AsyncIterator, Dict, List, Optional
import openai
from ..base import LLMProvider
from ...core.config import settings
from ...core.logging import logger

class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        provider = (settings.LLM_PROVIDER or "").lower()
        if provider == "groq" or (settings.GROQ_API_KEY and not settings.OPENAI_API_KEY and not settings.GEMINI_API_KEY):
            self.api_key = api_key or settings.GROQ_API_KEY
            self.model = model or getattr(settings, "GROQ_MODEL", None) or "qwen/qwen3.8-27b"
            self.client = openai.AsyncOpenAI(api_key=self.api_key, base_url=base_url or "https://api.groq.com/openai/v1") if self.api_key else None
        elif provider == "gemini" or (settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY and not settings.GROQ_API_KEY):
            self.api_key = api_key or settings.GEMINI_API_KEY
            self.model = model or "gemini-2.0-flash"
            self.client = openai.AsyncOpenAI(api_key=self.api_key, base_url=base_url or "https://generativelanguage.googleapis.com/v1beta/openai/") if self.api_key else None
        else:
            self.api_key = api_key or settings.OPENAI_API_KEY
            self.model = model or "gpt-4o-mini"
            self.client = openai.AsyncOpenAI(api_key=self.api_key, base_url=base_url) if self.api_key else None

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        if not self.client:
            logger.warning("LLM API key missing; falling back to MockLLMProvider")
            from .mock import MockLLMProvider
            async for ev in MockLLMProvider().stream(messages, tools):
                yield ev
            return

        formatted_messages = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                stream=True,
                temperature=0.7,
            )

            async for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield {"type": "text", "text": delta.content}
        except Exception as e:
            logger.error(f"Error calling LLM ({self.model}): {e}")
            yield {"type": "text", "text": f" [LLM Error: {str(e)}]"}

