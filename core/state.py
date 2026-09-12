from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class EntityState:
    """Estado interno transitório da entidade.

    Estes valores não afirmam emoções reais; representam variáveis funcionais
    que podem influenciar percepção, atenção, iniciativa e comportamento.
    """

    mode: str = "awake"
    attention: float = 0.5
    energy: float = 1.0
    mood: float = 0.0
    social_drive: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def clamp(self) -> None:
        self.attention = max(0.0, min(1.0, self.attention))
        self.energy = max(0.0, min(1.0, self.energy))
        self.mood = max(-1.0, min(1.0, self.mood))
        self.social_drive = max(0.0, min(1.0, self.social_drive))
