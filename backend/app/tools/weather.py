from typing import Any, Dict
from .registry import tool_registry

WEATHER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather conditions for a specified city or location",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city or locality name, e.g. Mumbai, New York, Buenos Aires"
                }
            },
            "required": ["city"]
        }
    }
}

async def get_weather(city: str) -> Dict[str, Any]:
    city_lower = city.lower()
    if "delhi" in city_lower:
        return {"city": "Delhi", "temperature_c": 28, "condition": "Hazy Sunshine", "humidity": "45%"}
    elif "mumbai" in city_lower:
        return {"city": "Mumbai", "temperature_c": 31, "condition": "Humid and Sunny", "humidity": "75%"}
    elif "buenos aires" in city_lower:
        return {"city": "Buenos Aires", "temperature_c": 19, "condition": "Partly Cloudy", "humidity": "60%"}
    elif "cairo" in city_lower:
        return {"city": "Cairo", "temperature_c": 26, "condition": "Clear and Sunny", "humidity": "35%"}
    else:
        return {"city": city, "temperature_c": 22, "condition": "Clear", "humidity": "50%"}

tool_registry.register("get_weather", WEATHER_SCHEMA, get_weather)

