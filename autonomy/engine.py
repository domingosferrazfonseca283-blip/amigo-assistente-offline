from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from core.entity import Entity
from core.lifecycle import Lifecycle
from core.runtime import Runtime
from mind import Mind
from nervous_system import Event, NervousSystem


@dataclass(frozen=True)
class AutonomyPolicy:
    """Limites funcionais da iniciativa da entidade."""

    enabled: bool = True
    observe_when_idle: bool = True
    max_events_per_cycle: int = 4
    max_actions_per_cycle: int = 1
    minimum_attention: float = 0.15


@dataclass
class AutonomyResult:
    timestamp: str
    lifecycle: str
    observed: bool
    event_count: int
    decision: str | None = None
    action: str = "none"
    action_payload: Any = None


@dataclass
class AutonomyEngine:
    """Executa ciclos de autonomia sem assumir consciência ou vontade real."""

    entity: Entity
    mind: Mind
    nervous_system: NervousSystem
    runtime: Runtime = field(default_factory=Runtime)
    policy: AutonomyPolicy = field(default_factory=AutonomyPolicy)
    observer: Callable[[], list[Event]] | None = None
    action_sink: Callable[[str, Any], Any] | None = None

    def start(self) -> None:
        self.entity.wake()
        self.runtime.wake()

    def stop(self) -> None:
        self.entity.sleep()
        self.runtime.sleep()

    def tick(self) -> AutonomyResult:
        timestamp = datetime.now(timezone.utc).isoformat()
        if not self.policy.enabled or self.entity.lifecycle.state is Lifecycle.SLEEPING:
            return AutonomyResult(timestamp, self.entity.lifecycle.state.value, False, 0)

        self.runtime.tick()
        observed = False
        if self.policy.observe_when_idle and self.observer is not None:
            for event in self.observer()[: self.policy.max_events_per_cycle]:
                self.nervous_system.emit(event)
            observed = True

        events: list[Event] = []
        while self.nervous_system._queue and len(events) < self.policy.max_events_per_cycle:
            events.append(self.nervous_system._queue.pop(0))

        # Ações geradas anteriormente nunca devem voltar a alimentar a própria
        # cognição neste ciclo, evitando loops act -> think -> act.
        cognitive_events = [event for event in events if not event.type.startswith("act.")]
        for event in events:
            for handler in self.nervous_system._handlers.get(event.type, []):
                handler(event)
            for handler in self.nervous_system._handlers.get("*", []):
                handler(event)

        if not events:
            self.runtime.idle()
            return AutonomyResult(timestamp, self.entity.lifecycle.state.value, observed, 0)

        self.entity.state.attention = max(
            self.policy.minimum_attention,
            min(1.0, self.entity.state.attention + 0.05),
        )

        thought = self.mind.think("", events=cognitive_events)
        action = thought.action or "none"
        payload = thought.action_payload
        if action != "none" and self.action_sink is not None:
            self.action_sink(action, payload)

        return AutonomyResult(
            timestamp,
            self.entity.lifecycle.state.value,
            observed,
            len(events),
            decision=thought.decision,
            action=action,
            action_payload=payload,
        )
