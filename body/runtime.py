from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nervous_system import Event, NervousSystem

from .interfaces import Actuator, Body, Sense


@dataclass
class BodyRuntime:
    """Liga o corpo universal ao sistema nervoso sem conhecer a plataforma."""

    body: Body
    nervous_system: NervousSystem
    last_perceptions: dict[str, Any] = field(default_factory=dict)

    def perceive(self, sense: Sense) -> Event:
        value = self.body.perceive(sense)
        self.last_perceptions[sense.value] = value
        event = Event(type=f"sense.{sense.value}", data={"sense": sense.value, "value": value})
        self.nervous_system.emit(event)
        return event

    def act(self, actuator: Actuator, payload: Any = None) -> Any:
        result = self.body.act(actuator, payload)
        self.nervous_system.emit(
            Event(
                type=f"act.{actuator.value}",
                data={"actuator": actuator.value, "payload": payload, "result": result},
            )
        )
        return result

    def perceive_available(self) -> list[Event]:
        return [self.perceive(sense) for sense in self.body.senses()]
