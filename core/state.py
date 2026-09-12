from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class EntityState:
    """Estado persistente e funcional da entidade, independente do hardware."""

    mode: str = "awake"
    mood: str = "calm"
    energy: float = 1.0
    attention: float = 0.5
    last_active_at: str | None = None
    internal: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.last_active_at = datetime.now(timezone.utc).isoformat()

    def set_energy(self, value: float) -> None:
        self.energy = max(0.0, min(1.0, value))
