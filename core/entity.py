from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from memory import MemoryKind, MemoryRecord, MemorySystem

from .identity import Identity
from .state import EntityState
from .lifecycle import LifecycleController, Lifecycle


@dataclass
class Entity:
    """Núcleo persistente da entidade, separado do dispositivo."""

    identity: Identity
    state: EntityState = field(default_factory=EntityState)
    lifecycle: LifecycleController = field(default_factory=LifecycleController)
    memory: MemorySystem | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def wake(self) -> None:
        self.lifecycle.transition(Lifecycle.AWAKE)
        self.state.mode = "awake"

    def sleep(self) -> None:
        self.lifecycle.transition(Lifecycle.SLEEPING)
        self.state.mode = "sleeping"

    def remember(
        self,
        content: str,
        *,
        kind: MemoryKind = MemoryKind.EPISODIC,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        if self.memory is None:
            raise RuntimeError("A memória persistente ainda não foi ligada a esta entidade.")
        return self.memory.remember(
            content,
            kind=kind,
            importance=importance,
            metadata=metadata,
        )

    def recall(self, query: str, limit: int = 10) -> list[MemoryRecord]:
        if self.memory is None:
            return []
        return self.memory.recall(query, limit=limit)

    def snapshot(self) -> dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "state": self.state.to_dict(),
            "lifecycle": self.lifecycle.state.value,
            "memory_records": self.memory.store.count() if self.memory is not None else 0,
            "created_at": self.created_at,
        }
