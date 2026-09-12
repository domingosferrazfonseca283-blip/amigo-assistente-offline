from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Identity:
    """Identidade persistente da entidade, independente do corpo/hardware."""

    entity_id: str
    name: str
    version: int = 1
    traits: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "version": self.version,
            "traits": self.traits,
        }
