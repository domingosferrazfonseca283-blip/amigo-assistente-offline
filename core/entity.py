from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .identity import EntityIdentity
from .state import EntityState


@dataclass
class Entity:
    """Representa a entidade como algo persistente, separado do seu corpo físico."""

    identity: EntityIdentity = field(default_factory=EntityIdentity)
    state: EntityState = field(default_factory=EntityState)
    metadata: dict[str, Any] = field(default_factory=dict)

    def awaken(self) -> None:
        self.state.mode = "awake"
        self.state.touch()

    def sleep(self) -> None:
        self.state.mode = "sleeping"
        self.state.touch()

    def snapshot(self) -> dict[str, Any]:
        return {
            "identity": self.identity.snapshot(),
            "state": {
                "mode": self.state.mode,
                "mood": self.state.mood,
                "energy": self.state.energy,
                "attention": self.state.attention,
                "last_active_at": self.state.last_active_at,
                "internal": dict(self.state.internal),
            },
            "metadata": dict(self.metadata),
        }
