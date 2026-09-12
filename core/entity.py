from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .identity import Identity
from .state import EntityState


@dataclass
class Entity:
    """Núcleo persistente da entidade, separado do dispositivo."""

    identity: Identity
    state: EntityState = field(default_factory=EntityState)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def snapshot(self) -> dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "state": self.state.to_dict(),
            "created_at": self.created_at,
        }
