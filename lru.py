#!/usr/bin/env python3
from typing import Any, Optional

class LRUCache:
    """
    A Least Recently Used (LRU) cache keeps items in the cache until it reaches its size
    and/or item limit (only item in our case). In which case, it removes an item that was accessed
    least recently.
    An item is considered accessed whenever `has`, `get`, or `set` is called with its key.

    Implement the LRU cache here and use the unit tests to check your implementation.
    """

    def __init__(self, item_limit: int):
        # TODO: implement this function
        raise NotImplementedError()

    def has(self, key: str) -> bool:
        # TODO: implement this function
        raise NotImplementedError()

    def get(self, key: str) -> Optional[Any]:
        # TODO: implement this function
        raise NotImplementedError()

    def set(self, key: str, value: Any):
        # TODO: implement this function
        raise NotImplementedError()
