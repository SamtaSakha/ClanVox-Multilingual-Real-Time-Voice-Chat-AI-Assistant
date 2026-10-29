from typing import Any, AsyncIterator, Dict, List, Optional
import openai
from ..base import LLMProvider
from ...core.config import settings
from ...core.logging import logger

class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        if not self.client:
            logger.warning("OpenAI API key missing; falling back to MockLLMProvider")
            from .mock import MockLLMProvider
            async for ev in MockLLMProvider().stream(messages, tools):
                yield ev
            return

        formatted_messages = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            stream=True,
            temperature=0.7,
        )

        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield {"type": "text", "text": delta.content}
