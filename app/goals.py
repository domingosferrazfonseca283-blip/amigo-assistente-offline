from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class GoalStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class Goal:
    title: str
    priority: float = 0.5
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0
    source: str = "internal"
    id: str = field(default_factory=lambda: uuid4().hex)
    notes: list[str] = field(default_factory=list)

    def advance(self, amount: float) -> None:
        self.progress = max(0.0, min(1.0, self.progress + amount))
        if self.progress >= 1.0:
            self.status = GoalStatus.COMPLETED


class GoalManager:
    def __init__(self) -> None:
        self.goals: dict[str, Goal] = {}

    def add(self, title: str, priority: float = 0.5, source: str = "internal") -> Goal:
        goal = Goal(title=title, priority=priority, source=source)
        self.goals[goal.id] = goal
        return goal

    def active(self) -> list[Goal]:
        return sorted(
            (g for g in self.goals.values() if g.status == GoalStatus.ACTIVE),
            key=lambda g: (g.priority, g.progress),
            reverse=True,
        )

    def top(self) -> Goal | None:
        goals = self.active()
        return goals[0] if goals else None
