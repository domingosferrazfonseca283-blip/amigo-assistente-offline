from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .perception import Perception, PerceptionEngine, PerceptionType


class AndroidContextSource(Protocol):
    """Adaptador implementado pela camada Android/Kotlin."""

    def snapshot(self) -> dict[str, Any]:
        ...


@dataclass
class LocalContextBridge:
    perception: PerceptionEngine
    source: AndroidContextSource | None = None
    enabled: set[PerceptionType] = field(default_factory=lambda: {
        PerceptionType.DEVICE,
        PerceptionType.NOTIFICATION,
        PerceptionType.APP,
        PerceptionType.TIME,
        PerceptionType.SYSTEM,
    })

    def poll(self) -> list[Perception]:
        if self.source is None:
            return []
        snapshot = self.source.snapshot()
        result: list[Perception] = []
        for name, value in snapshot.items():
            try:
                kind = PerceptionType(name)
            except ValueError:
                kind = PerceptionType.SYSTEM
            if kind not in self.enabled and kind != PerceptionType.SYSTEM:
                continue
            result.append(self.perception.ingest(Perception(kind, {"value": value}, 0.9, "android")))
        return result
