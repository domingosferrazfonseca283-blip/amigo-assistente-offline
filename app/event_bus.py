from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from threading import RLock

from .cognitive_events import CognitiveEvent, EventType

Handler = Callable[[CognitiveEvent], None]


class EventBus:
    """Barramento local síncrono; a persistência fica separada do transporte."""

    def __init__(self, history_limit: int = 5000) -> None:
        self._handlers: dict[EventType, list[Handler]] = defaultdict(list)
        self._history: deque[CognitiveEvent] = deque(maxlen=history_limit)
        self._lock = RLock()

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        with self._lock:
            self._handlers[event_type].append(handler)

    def publish(self, event: CognitiveEvent) -> None:
        with self._lock:
            self._history.append(event)
            handlers = tuple(self._handlers.get(event.type, ()))
        for handler in handlers:
            handler(event)

    def recent(self, limit: int = 100) -> list[CognitiveEvent]:
        with self._lock:
            return list(self._history)[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._history.clear()
