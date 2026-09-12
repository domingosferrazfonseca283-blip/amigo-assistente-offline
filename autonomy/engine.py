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
    """Executa ciclos curtos de autonomia sem assumir consciência ou vontade real."""

    entity: Entity
    mind: Mind
    nervous_system: NervousSystem
    runtime: Runtime = field(default_factory=Runtime)
    policy: AutonomyPolicy = field(default_factory=AutonomyPolicy)
    observer: Callable[[], list[Event]] | None = None

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
            for event in self.observer()[: self.policy.max_actions_per_cycle]:
                self.nervous_system.emit(event)
            observed = True

        before = self.nervous_system.dispatch()
        events: list[Event] = []
        if self.observer is not None:
            # Events emitted by the observer have already passed through the queue;
            # autonomy records their count without owning the hardware itself.
            events = []

        if before == 0:
            self.runtime.idle()
            return AutonomyResult(timestamp, self.entity.lifecycle.state.value, observed, 0)

        self.entity.state.attention = max(
            self.policy.minimum_attention,
            min(1.0, self.entity.state.attention + 0.05),
        )
        return AutonomyResult(
            timestamp,
            self.entity.lifecycle.state.value,
            observed,
            before,
            decision="processar eventos recebidos",
        )
