from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .agency import AgencyEngine, Initiative
from .goals import GoalManager


@dataclass
class InitiativePolicy:
    enabled: bool = True
    min_priority: float = 0.70
    cooldown_seconds: int = 300
    require_confirmation: bool = True
    max_pending: int = 3


class InitiativeEngine:
    """Permite iniciativa proativa apenas quando a política local autoriza."""

    def __init__(self, goals: GoalManager, agency: AgencyEngine, policy: InitiativePolicy | None = None) -> None:
        self.goals = goals
        self.agency = agency
        self.policy = policy or InitiativePolicy()
        self._last_generated: datetime | None = None
        self.pending: list[Initiative] = []

    def evaluate(self, context: str = "inatividade") -> Initiative | None:
        if not self.policy.enabled or len(self.pending) >= self.policy.max_pending:
            return None
        now = datetime.now(timezone.utc)
        if self._last_generated is not None and now - self._last_generated < timedelta(seconds=self.policy.cooldown_seconds):
            return None
        goal = self.goals.top()
        if goal is None or goal.priority < self.policy.min_priority:
            return None
        initiative = self.agency.request_initiative(goal, context)
        if initiative is None:
            return None
        if self.policy.require_confirmation:
            initiative.requires_confirmation = True
        self.pending.append(initiative)
        self._last_generated = now
        return initiative

    def approve(self, index: int = 0) -> Initiative | None:
        if not self.pending or index < 0 or index >= len(self.pending):
            return None
        return self.pending.pop(index)

    def reject(self, index: int = 0) -> Initiative | None:
        return self.approve(index)
