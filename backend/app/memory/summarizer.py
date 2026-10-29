from typing import List
from ..schemas.chat import ChatMessage

class ConversationSummarizer:
    """Summarizes conversation history when turn length exceeds window thresholds."""

    def summarize_turns(self, history: List[ChatMessage]) -> str:
        if len(history) < 6:
            return ""

        summary_points = []
        for msg in history[:-2]:
            summary_points.append(f"{msg.role}: {msg.content[:60]}...")
        return "Previous context: " + " | ".join(summary_points)

