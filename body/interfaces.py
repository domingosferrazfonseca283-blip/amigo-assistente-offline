from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Sense:
    """Percepção abstrata produzida por um sentido do corpo."""

    kind: str
    data: Any
    timestamp: float
    source: str


class Vision(Protocol):
    def capture(self) -> Sense: ...


class Hearing(Protocol):
    def listen(self, seconds: float | None = None) -> Sense: ...


class Speech(Protocol):
    def speak(self, text: str) -> None: ...


class Vibration(Protocol):
    def vibrate(self, duration_ms: int = 100) -> None: ...


class Body(Protocol):
    """Contrato que qualquer dispositivo pode implementar."""

    def available_senses(self) -> set[str]: ...

    def available_capabilities(self) -> set[str]: ...

    def sense(self, name: str, **kwargs: Any) -> Sense: ...

    def act(self, name: str, **kwargs: Any) -> Any: ...
