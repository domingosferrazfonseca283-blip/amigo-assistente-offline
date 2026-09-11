from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable
from uuid import uuid4

from .autonomy_scheduler import AutonomyScheduler, InternalTask
from .cognitive_events import CognitiveEvent, EventType


class InternalActivity(StrEnum):
    REVIEW_GOALS = "review_goals"
    REVIEW_EXPECTATIONS = "review_expectations"
    REFLECT = "reflect"
    CONSOLIDATE = "consolidate"
    IDLE = "idle"


@dataclass
class InternalCycleResult:
    activity: InternalActivity
    task_id: str | None
    summary: str
    changed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class InternalLifePolicy:
    enabled: bool = True
    min_idle_seconds: float = 60.0
    max_cycles_per_wake: int = 1
    max_internal_seconds: float = 2.0


class InternalLife:
    """Orquestra actividade cognitiva sem interação do utilizador.

    Não cria acesso ao sistema nem permissões novas. Cada ciclo é limitado por
    orçamento e deve ser disparado pelo hospedeiro (Android, teste ou serviço).
    """

    def __init__(
        self,
        scheduler: AutonomyScheduler,
        *,
        policy: InternalLifePolicy | None = None,
        event_sink: Callable[[CognitiveEvent], Any] | None = None,
    ) -> None:
        self.scheduler = scheduler
        self.policy = policy or InternalLifePolicy()
        self.event_sink = event_sink
        self.cycles: list[InternalCycleResult] = []
        self.last_activity_at: str | None = None

    def _emit(self, result: InternalCycleResult) -> None:
        if self.event_sink is not None:
            self.event_sink(CognitiveEvent(
                EventType.REFLECTION,
                {"activity": result.activity.value, "task_id": result.task_id, "summary": result.summary, "changed": result.changed},
                source="internal_life",
                importance=0.55,
            ))

    def tick(self, *, curiosity: float, uncertainty: float, novelty: float) -> list[InternalCycleResult]:
        if not self.policy.enabled:
            return []
        self.scheduler.budget.reset()
        tasks = self.scheduler.from_current_state(curiosity, uncertainty, novelty)
        selected = self.scheduler.propose(tasks)
        results: list[InternalCycleResult] = []
        for task in selected[: self.policy.max_cycles_per_wake]:
            activity = {
                "goal": InternalActivity.REVIEW_GOALS,
                "curiosity": InternalActivity.REVIEW_EXPECTATIONS,
                "anomaly": InternalActivity.REFLECT,
                "maintenance": InternalActivity.CONSOLIDATE,
                "relationship": InternalActivity.REFLECT,
            }.get(task.reason.value, InternalActivity.REFLECT)
            result = InternalCycleResult(activity, task.id, task.title, changed=False)
            self.cycles.append(result)
            self.scheduler.complete(task.id)
            self._emit(result)
            results.append(result)
        self.cycles = self.cycles[-500:]
        self.last_activity_at = datetime.now(timezone.utc).isoformat() if results else self.last_activity_at
        return results

    def snapshot(self) -> dict[str, Any]:
        return {
            "policy": asdict(self.policy),
            "last_activity_at": self.last_activity_at,
            "cycles": [asdict(item) | {"activity": item.activity.value} for item in self.cycles[-100:]],
        }
