from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass(frozen=True)
class Event:
    type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NervousSystem:
    """Canal entre o corpo, a mente e os acontecimentos do ambiente."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[Event], None]]] = {}
        self._queue: list[Event] = []

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(self, event: Event) -> None:
        self._queue.append(event)

    def dispatch(self) -> int:
        count = 0
        while self._queue:
            event = self._queue.pop(0)
            for handler in self._handlers.get(event.type, []):
                handler(event)
            for handler in self._handlers.get("*", []):
                handler(event)
            count += 1
        return count
