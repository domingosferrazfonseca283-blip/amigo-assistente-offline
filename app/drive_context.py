from __future__ import annotations

from dataclasses import dataclass

from .noemia_being import BeingDrive, NoemiaBeing


@dataclass(frozen=True)
class DriveContext:
    """Contexto cognitivo derivado dos impulsos internos da Noémia.

    Drives influenceiam atenção e escolha de objetivos, mas não executam ações.
    Esta separação mantém a diferença entre impulso, objetivo e ação.
    """

    dominant: BeingDrive | None
    drives: tuple[BeingDrive, ...]
    focus: str | None
    reason: str | None

    @classmethod
    def from_being(cls, being: NoemiaBeing, limit: int = 3) -> "DriveContext":
        ranked = tuple(being.drives(limit))
        dominant = ranked[0] if ranked else None
        return cls(
            dominant=dominant,
            drives=ranked,
            focus=being.current_focus,
            reason=dominant.reason if dominant else None,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "dominant": self.dominant.name if self.dominant else None,
            "intensity": self.dominant.intensity if self.dominant else 0.0,
            "focus": self.focus,
            "reason": self.reason,
            "drives": [
                {
                    "name": drive.name,
                    "intensity": drive.intensity,
                    "reason": drive.reason,
                    "suggested_focus": drive.suggested_focus,
                }
                for drive in self.drives
            ],
        }
