from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .cognitive_runtime import CognitiveRuntime
from .cognitive_events import CognitiveEvent, EventType
from .noemia_being import NoemiaBeing


@dataclass
class NoemiaLife:
    """Orquestrador da continuidade da Noémia sobre o CognitiveRuntime."""

    runtime: CognitiveRuntime

    def __post_init__(self) -> None:
        self.being = NoemiaBeing()
        self.runtime.bus.subscribe(EventType.USER_MESSAGE, self._experience)
        self.runtime.bus.subscribe(EventType.MODEL_RESPONSE, self._experience)
        self.runtime.bus.subscribe(EventType.DECISION, self._experience)
        self.runtime.bus.subscribe(EventType.CONSOLIDATION, self._experience)

    def _experience(self, event: CognitiveEvent) -> None:
        self.being.experience(event)

    def think(self, text: str) -> str:
        self.being.pulse("experiência recebida", "thinking", ["conversation"])
        response = self.runtime.think(text)
        self.being.set_focus(None)
        self.being.pulse("experiência integrada", "expressing", ["response", "memory"])
        return response

    def internal_cycle(self, reason: str = "continuidade") -> dict[str, Any]:
        pulse = self.being.pulse(reason, "reflecting", ["internal_cycle"])
        self.runtime.run_consolidation()
        return {
            "pulse": pulse.__dict__.copy(),
            "being": self.being.snapshot(),
            "runtime": self.runtime.snapshot(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "being": self.being.snapshot(),
            "runtime": self.runtime.snapshot(),
        }

    def restore_being(self, snapshot: dict[str, Any]) -> None:
        self.being = NoemiaBeing.restore(snapshot)
