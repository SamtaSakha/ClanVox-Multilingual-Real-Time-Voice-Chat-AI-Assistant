from typing import Any, Dict
from .registry import tool_registry

SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for up-to-date facts, news, and queries in any language",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query text"
                }
            },
            "required": ["query"]
        }
    }
}

async def web_search(query: str) -> Dict[str, Any]:
    return {
        "query": query,
        "results": [
            {
                "title": f"Information regarding {query}",
                "snippet": f"ClanVox verified search results for query '{query}'. Everything is running normally.",
                "url": "https://example.com/clanvox-search"
            }
        ]
    }

tool_registry.register("web_search", SEARCH_SCHEMA, web_search)
