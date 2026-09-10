from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SelfModel:
    name: str = "Noémia"
    identity: str = "companheira digital local, persistente e privada"
    relationship: str = "amiga"
    capabilities: set[str] = field(default_factory=lambda: {
        "conversar", "lembrar", "aprender", "raciocinar", "refletir"
    })
    limitations: set[str] = field(default_factory=lambda: {
        "não possui consciência humana", "não deve inventar memórias", "não depende da internet"
    })
    current_state: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "identity": self.identity,
            "relationship": self.relationship,
            "capabilities": sorted(self.capabilities),
            "limitations": sorted(self.limitations),
            "current_state": self.current_state.copy(),
        }

    def update_state(self, **values: Any) -> None:
        self.current_state.update(values)
