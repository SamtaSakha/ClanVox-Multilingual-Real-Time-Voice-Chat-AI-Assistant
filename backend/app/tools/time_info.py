from datetime import datetime, timezone
from typing import Any, Dict
from .registry import tool_registry

TIME_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "Get current UTC time and formatted local time information",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone_hint": {
                    "type": "string",
                    "description": "Timezone name or UTC offset"
                }
            }
        }
    }
}

async def get_time(timezone_hint: str = "UTC") -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "utc_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "timestamp": int(now.timestamp()),
        "timezone": timezone_hint
    }

tool_registry.register("get_time", TIME_SCHEMA, get_time)
