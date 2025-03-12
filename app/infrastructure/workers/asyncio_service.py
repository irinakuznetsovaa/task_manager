import asyncio
from typing import Any, Coroutine

def run_async_function(coro: Coroutine[Any, Any, Any]) -> Any:

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return loop.run_until_complete(coro)