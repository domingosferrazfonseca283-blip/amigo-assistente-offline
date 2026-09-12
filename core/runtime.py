from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .lifecycle import Lifecycle, LifecycleController
from .state import EntityState


@dataclass
class Runtime:
    """Ciclo operacional da entidade: acordar, observar, agir e repousar."""

    state: EntityState = field(default_factory=EntityState)
    lifecycle: LifecycleController = field(default_factory=LifecycleController)
    last_tick: str | None = None

    def wake(self) -> None:
        self.lifecycle.transition(Lifecycle.AWAKE)
        self.state.mode = "awake"

    def idle(self) -> None:
        self.lifecycle.transition(Lifecycle.IDLE)
        self.state.mode = "idle"

    def sleep(self) -> None:
        self.lifecycle.transition(Lifecycle.SLEEPING)
        self.state.mode = "sleeping"

    def offline(self) -> None:
        self.lifecycle.transition(Lifecycle.OFFLINE)
        self.state.mode = "offline"

    def tick(self) -> dict[str, Any]:
        self.last_tick = datetime.now(timezone.utc).isoformat()
        self.state.clamp()
        return {
            "lifecycle": self.lifecycle.state.value,
            "state": self.state.to_dict(),
            "timestamp": self.last_tick,
        }
