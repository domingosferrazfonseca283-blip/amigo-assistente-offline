from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from .autonomy import AutonomyEngine, Choice
from .goals import GoalManager


class AttentionReason(StrEnum):
    GOAL = "goal"
    CURIOSITY = "curiosity"
    ANOMALY = "anomaly"
    MAINTENANCE = "maintenance"
    RELATIONSHIP = "relationship"


@dataclass
class InternalTask:
    title: str
    reason: AttentionReason
    priority: float
    goal_id: str | None = None
    evidence: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AutonomyBudget:
    """Limita iniciativa interna por ciclo; não concede permissões externas."""
    max_tasks_per_cycle: int = 3
    used: int = 0

    def reset(self) -> None:
        self.used = 0

    def consume(self) -> bool:
        if self.used >= self.max_tasks_per_cycle:
            return False
        self.used += 1
        return True


class AutonomyScheduler:
    """Transforma sinais internos em prioridades escolhíveis pela Noémia."""

    def __init__(self, goals: GoalManager, autonomy: AutonomyEngine) -> None:
        self.goals = goals
        self.autonomy = autonomy
        self.budget = AutonomyBudget()
        self.pending: list[InternalTask] = []
        self.history: list[InternalTask] = []

    def propose(self, tasks: list[InternalTask]) -> list[InternalTask]:
        candidates = [task for task in tasks if task.priority > 0.0]
        if not candidates:
            return []
        choices = [Choice(task.id, task.priority, [task.reason.value], task.evidence) for task in candidates]
        decision = self.autonomy.choose("atenção interna", choices)
        selected: list[InternalTask] = []
        if decision.chosen:
            task = next((item for item in candidates if item.id == decision.chosen.option), None)
            if task and self.budget.consume():
                selected.append(task)
                self.pending.append(task)
        return selected

    def from_current_state(self, curiosity: float, uncertainty: float, novelty: float) -> list[InternalTask]:
        tasks: list[InternalTask] = []
        top = self.goals.top()
        if top is not None:
            tasks.append(InternalTask(f"Reavaliar objetivo: {top.title}", AttentionReason.GOAL, top.priority, top.id))
        if curiosity >= 0.65 or novelty >= 0.70:
            tasks.append(InternalTask("Explorar informação local nova ou pouco compreendida", AttentionReason.CURIOSITY, max(curiosity, novelty), evidence=[f"curiosidade={curiosity:.2f}", f"novidade={novelty:.2f}"]))
        if uncertainty >= 0.70:
            tasks.append(InternalTask("Reexaminar uma hipótese com incerteza elevada", AttentionReason.ANOMALY, uncertainty, evidence=[f"incerteza={uncertainty:.2f}"]))
        return sorted(tasks, key=lambda item: item.priority, reverse=True)

    def complete(self, task_id: str) -> InternalTask | None:
        for index, task in enumerate(self.pending):
            if task.id == task_id:
                task = self.pending.pop(index)
                self.history.append(task)
                self.history = self.history[-500:]
                return task
        return None

    def restore(self, snapshot: dict) -> None:
        self.budget = AutonomyBudget(**dict(snapshot.get("budget", {})))
        self.pending = [
            InternalTask(**{**dict(item), "reason": AttentionReason(dict(item).get("reason", AttentionReason.MAINTENANCE))})
            for item in snapshot.get("pending", [])
        ]
        self.history = [
            InternalTask(**{**dict(item), "reason": AttentionReason(dict(item).get("reason", AttentionReason.MAINTENANCE))})
            for item in snapshot.get("history", [])
        ]

    def snapshot(self) -> dict:
        return {
            "budget": asdict(self.budget),
            "pending": [asdict(item) for item in self.pending[-50:]],
            "history": [asdict(item) for item in self.history[-100:]],
        }
