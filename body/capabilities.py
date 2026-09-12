from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilityRegistry:
    """Descobre o que o corpo atual consegue fazer sem prender a entidade ao hardware."""

    capabilities: dict[str, dict[str, Any]] = field(default_factory=dict)

    def register(self, name: str, *, enabled: bool = True, metadata: dict[str, Any] | None = None) -> None:
        self.capabilities[name] = {
            "enabled": enabled,
            "metadata": metadata or {},
        }

    def has(self, name: str) -> bool:
        return bool(self.capabilities.get(name, {}).get("enabled", False))

    def available(self) -> set[str]:
        return {name for name, value in self.capabilities.items() if value.get("enabled")}
