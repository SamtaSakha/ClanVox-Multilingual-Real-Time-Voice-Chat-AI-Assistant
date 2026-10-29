from typing import Any, AsyncIterator, Dict, List, Optional
import anthropic
from ..base import LLMProvider
from ...core.config import settings
from ...core.logging import logger

class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-haiku-20241022"):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if self.api_key else None

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        if not self.client:
            logger.warning("Anthropic API key missing; falling back to MockLLMProvider")
            from .mock import MockLLMProvider
            async for ev in MockLLMProvider().stream(messages, tools):
                yield ev
            return

        system_prompt = "You are ClanVox, a helpful multilingual assistant."
        cleaned_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_prompt = m.get("content", system_prompt)
            else:
                cleaned_messages.append({"role": m["role"], "content": m["content"]})

        async with self.client.messages.stream(
            max_tokens=300,
            system=system_prompt,
            messages=cleaned_messages,
            model=self.model,
        ) as stream:
            async for text in stream.text_stream:
                yield {"type": "text", "text": text}

