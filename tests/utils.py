# Utility functions to make testing easier
import asyncio
from typing import Any, Awaitable


def run_coroutine(result: Awaitable[Any]) -> Any:
    """Wrapper for asyncio functions to allow them to be run from synchronous functions"""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(result)
    loop.close()
    return result


def make_awaitable(result: Any) -> Awaitable[Any]:
    """
    Makes an awaitable, suitable for mocking an `async` function.
    This uses Futures as they can be awaited multiple times so can be returned
    to multiple callers.
    """
    future = asyncio.Future()  # type: ignore
    future.set_result(result)
    return future
