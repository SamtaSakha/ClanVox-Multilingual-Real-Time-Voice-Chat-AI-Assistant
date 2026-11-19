import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional
from ..base import LLMProvider

class MockLLMProvider(LLMProvider):
    def __init__(self, latency_per_token: float = 0.005):
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

        lower = last_message.lower().strip()

        # Tool calling demonstration if asked about weather
        if any(w in lower for w in ["weather", "mausam", "clima", "temperature"]):
            city = "Delhi" if "delhi" in lower else "Mumbai" if "mumbai" in lower else "New York"
            yield {
                "type": "tool_call",
                "name": "get_weather",
                "args": {"city": city}
            }
            return

        # Tool calling demonstration if asked about time
        if any(t in lower for t in ["what time", "current time", "samay", "time now", "what's the time"]):
            yield {
                "type": "tool_call",
                "name": "get_time",
                "args": {"timezone_hint": "UTC"}
            }
            return

        # Natural conversational replies
        if "how are you" in lower or "how r u" in lower:
            reply = "Hello! I am doing wonderful, thank you for asking. How are you doing today, and how can I help you?"
        elif any(lower.startswith(g) or lower == g for g in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]):
            reply = "Hello! Welcome to ClanVox. I am your real-time multilingual assistant. What would you like to explore today?"
        elif any(w in lower for w in ["who are you", "what are you", "what can you do", "introduce yourself"]):
            reply = "I am ClanVox, a real-time multilingual AI assistant designed for fluid voice and text conversation with automatic language detection, code-switching, and tool calling."
        elif any(w in lower for w in ["thank", "thanks", "dhanyawad", "shukriya"]):
            reply = "You're very welcome! Always happy to help. Let me know if you need anything else."
        elif any(w in lower for w in ["bye", "goodbye", "see you", "alvida"]):
            reply = "Goodbye! Take care and have a wonderful day ahead!"
        elif "joke" in lower:
            reply = "Why do programmers prefer dark mode? Because light attracts bugs!"
        # Multilingual conversational replies
        elif any(h in lower for h in ["namaste", "kaise ho", "kya chal", "aap kaise"]):
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
            reply = (
                f"I received your message: '{last_message}'. "
                "I am currently running in offline demo mode. To enable full generative AI answers for any query, "
                "please configure an API key (such as Groq, Gemini, or OpenAI) in your .env file."
            )

        words = reply.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else " " + word
            await asyncio.sleep(self.latency)
            yield {"type": "text", "text": chunk}

