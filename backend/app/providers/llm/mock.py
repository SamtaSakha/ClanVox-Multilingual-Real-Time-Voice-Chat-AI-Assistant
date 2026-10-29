import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional
from ..base import LLMProvider

class MockLLMProvider(LLMProvider):
    def __init__(self, latency_per_token: float = 0.03):
        self.latency = latency_per_token

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        last_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_message = m.get("content", "")
                break

        lower = last_message.lower()

        # Tool calling demonstration if asked about weather
        if "weather" in lower or "mausam" in lower or "clima" in lower:
            city = "Delhi" if "delhi" in lower else "Mumbai" if "mumbai" in lower else "New York"
            yield {
                "type": "tool_call",
                "name": "get_weather",
                "args": {"city": city}
            }
            return

        # Multilingual conversational replies
        if any(h in lower for h in ["namaste", "kaise ho", "kya chal", "aap kaise"]):
            reply = "Namaste! Main badhiya hoon. Aap bataiye, aaj main aapki kya madad kar sakta hoon?"
        elif any(s in lower for s in ["hola", "cómo estás", "buenos días", "que tal"]):
            reply = "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué te puedo colaborar hoy?"
        elif any(f in lower for f in ["bonjour", "comment ça va", "salut"]):
            reply = "Bonjour ! Tout va bien, merci. Comment puis-je vous aider aujourd'hui ?"
        elif any(a in lower for a in ["marhaba", "ezzayak", "sabah el kheir"]):
            reply = "أهلاً بك! أنا بخير والحمد لله. كيف يمكنني مساعدتك اليوم؟"
        elif "laptop" in lower or "screen" in lower:
            reply = "I understand your screen is having issues. Please check if the power indicator light is on or blinking."
        else:
            reply = f"Hello! I am ClanVox, your real-time multilingual AI assistant. You said: '{last_message}'."

        words = reply.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else " " + word
            await asyncio.sleep(self.latency)
            yield {"type": "text", "text": chunk}
