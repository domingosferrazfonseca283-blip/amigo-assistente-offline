from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4


class AutonomyLevel(StrEnum):
    OBSERVE = "observe"
    SUGGEST = "suggest"
    CHOOSE = "choose"
    ACT = "act"


@dataclass
class Choice:
    option: str
    score: float
    reasons: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class AutonomyDecision:
    goal: str
    chosen: Choice | None
    alternatives: list[Choice]
    autonomy_level: AutonomyLevel
    requires_confirmation: bool
    rationale: str
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class AutonomyPolicy:
    """Liberdade operacional configurável; segurança e permissões continuam separadas."""
    level: AutonomyLevel = AutonomyLevel.CHOOSE
    allow_background_reasoning: bool = True
    allow_self_initiated_goals: bool = True
    require_confirmation_for_external_actions: bool = True
    max_action_risk: str = "low"


class AutonomyEngine:
    """Escolhe entre alternativas reais e respeita o limite de risco configurado."""

    _RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}

    def __init__(self, policy: AutonomyPolicy | None = None) -> None:
        self.policy = policy or AutonomyPolicy()
        self.decisions: list[AutonomyDecision] = []

    def choose(self, goal: str, choices: list[Choice]) -> AutonomyDecision:
        allowed = [choice for choice in choices if self._risk_allowed(choice)]
        ranked = sorted(allowed, key=lambda item: item.score, reverse=True)
        chosen = ranked[0] if ranked and self.policy.level in {AutonomyLevel.CHOOSE, AutonomyLevel.ACT} else None
        confirmation = self.policy.require_confirmation_for_external_actions
        if chosen is not None and chosen.risks:
            confirmation = True
        rationale = "Escolha baseada nas alternativas, histórico operacional, razões e riscos disponíveis."
        decision = AutonomyDecision(goal, chosen, ranked[1:], self.policy.level, confirmation, rationale)
        self.decisions.append(decision)
        self.decisions = self.decisions[-500:]
        return decision

    def _risk_allowed(self, choice: Choice) -> bool:
        max_level = self._RISK_ORDER.get(self.policy.max_action_risk, 1)
        return not choice.risks or max_level >= 1

    def should_create_goal(self, priority: float) -> bool:
        return self.policy.allow_self_initiated_goals and priority >= 0.70

    def snapshot(self) -> dict[str, Any]:
        return {"policy": asdict(self.policy), "decisions": [asdict(item) for item in self.decisions[-100:]]}
