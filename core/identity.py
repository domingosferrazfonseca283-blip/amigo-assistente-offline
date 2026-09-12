from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
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

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "Identity":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            entity_id=str(data["entity_id"]),
            name=str(data["name"]),
            version=int(data.get("version", 1)),
            traits=dict(data.get("traits", {})),
        )

    @classmethod
    def load_or_create(
        cls,
        path: str | Path = "data/entity_identity.json",
        *,
        name: str = "Noémia",
        traits: dict[str, Any] | None = None,
    ) -> "Identity":
        target = Path(path)
        if target.exists():
            return cls.load(target)

        from uuid import uuid4

        identity = cls(
            entity_id=str(uuid4()),
            name=name,
            traits=traits or {"entity_type": "artificial_companion"},
        )
        identity.save(target)
        return identity
