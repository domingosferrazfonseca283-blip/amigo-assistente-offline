from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass(frozen=True)
class Event:
    """Algo que aconteceu ao corpo ou ao mundo e que pode merecer atenção."""

    kind: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)
    source: str = "unknown"
    priority: float = 0.5


class EventBus:
    def __init__(self) -> None:
        self._events: list[Event] = []

    def publish(self, event: Event) -> None:
        self._events.append(event)

    def drain(self) -> list[Event]:
        events = list(self._events)
        self._events.clear()
        return events
