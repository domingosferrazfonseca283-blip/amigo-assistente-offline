from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class Sense(str, Enum):
    VISION = "vision"
    HEARING = "hearing"
    TOUCH = "touch"
    MOTION = "motion"
    LOCATION = "location"
    LIGHT = "light"
    PROXIMITY = "proximity"
    TEMPERATURE = "temperature"


class Actuator(str, Enum):
    SPEECH = "speech"
    DISPLAY = "display"
    VIBRATION = "vibration"
    CAMERA = "camera"
    NOTIFICATION = "notification"


class BodyAdapter(Protocol):
    """Implementação do corpo num dispositivo concreto."""

    def has_sense(self, sense: Sense) -> bool: ...
    def sense(self, sense: Sense) -> Any: ...
    def can_act(self, actuator: Actuator) -> bool: ...
    def act(self, actuator: Actuator, payload: Any = None) -> Any: ...


@dataclass
class Body:
    """Corpo universal. Não conhece Android, iOS ou hardware específico."""

    adapter: BodyAdapter
    metadata: dict[str, Any] = field(default_factory=dict)

    def senses(self) -> list[Sense]:
        return [sense for sense in Sense if self.adapter.has_sense(sense)]

    def capabilities(self) -> list[Actuator]:
        return [actuator for actuator in Actuator if self.adapter.can_act(actuator)]

    def perceive(self, sense: Sense) -> Any:
        if not self.adapter.has_sense(sense):
            raise RuntimeError(f"Sentido indisponível neste corpo: {sense.value}")
        return self.adapter.sense(sense)

    def act(self, actuator: Actuator, payload: Any = None) -> Any:
        if not self.adapter.can_act(actuator):
            raise RuntimeError(f"Capacidade indisponível neste corpo: {actuator.value}")
        return self.adapter.act(actuator, payload)
