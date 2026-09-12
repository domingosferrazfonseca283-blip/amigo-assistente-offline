from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .identity import Identity
from .state import EntityState
from .lifecycle import LifecycleController, Lifecycle


@dataclass
class Entity:
    """Núcleo persistente da entidade, separado do dispositivo."""

    identity: Identity
    state: EntityState = field(default_factory=EntityState)
    lifecycle: LifecycleController = field(default_factory=LifecycleController)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def wake(self) -> None:
        self.lifecycle.transition(Lifecycle.AWAKE)
        self.state.mode = "awake"

    def sleep(self) -> None:
        self.lifecycle.transition(Lifecycle.SLEEPING)
        self.state.mode = "sleeping"

    def snapshot(self) -> dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "state": self.state.to_dict(),
            "lifecycle": self.lifecycle.state.value,
            "created_at": self.created_at,
        }
