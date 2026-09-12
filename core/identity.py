from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntityIdentity:
    """Identidade da entidade; não depende do modelo nem do dispositivo."""

    entity_id: str = "amigo"
    name: str = "Amigo"
    version: int = 1
    traits: dict[str, Any] = field(default_factory=lambda: {
        "role": "companion",
        "relationship": "exclusive_user",
    })

    def snapshot(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "version": self.version,
            "traits": dict(self.traits),
        }
