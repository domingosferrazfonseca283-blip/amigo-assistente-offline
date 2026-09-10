from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class PerceptionType(StrEnum):
    USER_INPUT = "user_input"
    DEVICE = "device"
    NOTIFICATION = "notification"
    AUDIO = "audio"
    APP = "app"
    TIME = "time"
    SENSOR = "sensor"
    LOCATION = "location"
    SYSTEM = "system"


@dataclass
class Perception:
    kind: PerceptionType
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = "local"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


class PerceptionEngine:
    """Entrada sensorial abstrata. Não acede ao Android diretamente."""

    def __init__(self) -> None:
        self.history: list[Perception] = []
        self.max_history = 2000

    def ingest(self, perception: Perception) -> Perception:
        perception.confidence = max(0.0, min(1.0, float(perception.confidence)))
        self.history.append(perception)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        return perception

    def user_text(self, text: str) -> Perception:
        return self.ingest(Perception(PerceptionType.USER_INPUT, {"text": text}, 1.0, "user"))

    def recent(self, kind: PerceptionType | None = None, limit: int = 20) -> list[Perception]:
        items = self.history if kind is None else [p for p in self.history if p.kind == kind]
        return items[-limit:]

    def snapshot(self) -> list[dict[str, Any]]:
        return [
            {
                "id": p.id,
                "kind": p.kind.value,
                "data": p.data,
                "confidence": p.confidence,
                "source": p.source,
                "timestamp": p.timestamp,
            }
            for p in self.history
        ]
