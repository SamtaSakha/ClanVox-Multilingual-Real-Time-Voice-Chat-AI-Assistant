from typing import Any, Callable, Coroutine, Dict, List, Optional
from ..core.logging import logger

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[..., Coroutine[Any, Any, Dict[str, Any]]]] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, name: str, schema: Dict[str, Any], func: Callable[..., Coroutine[Any, Any, Dict[str, Any]]]):
        self._tools[name] = func
        self._schemas.append(schema)

    def get_schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

    async def execute(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            return {"error": f"Tool '{name}' not found"}
        try:
            handler = self._tools[name]
            result = await handler(**args)
            return result
        except Exception as e:
            logger.error("Tool execution failed", tool=name, error=str(e))
            return {"error": str(e)}

tool_registry = ToolRegistry()
