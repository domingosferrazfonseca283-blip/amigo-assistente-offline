from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4

from .goals import Goal


class ActionRisk(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PermissionMode(StrEnum):
    DENY = "deny"
    CONFIRM = "confirm"
    ALLOW = "allow"


@dataclass
class ActionCapability:
    name: str
    description: str
    risk: ActionRisk = ActionRisk.LOW
    permission: PermissionMode = PermissionMode.CONFIRM
    background_allowed: bool = False
    enabled: bool = True


@dataclass
class PlanStep:
    action: str
    reason: str
    risk: ActionRisk = ActionRisk.LOW
    requires_confirmation: bool = True
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class Plan:
    goal_id: str
    steps: list[PlanStep]
    confidence: float = 0.5


@dataclass
class Initiative:
    reason: str
    goal_id: str | None
    action: str
    requires_confirmation: bool


class AgencyEngine:
    """Transforma objetivos em planos sem inventar capacidades ou permissões."""

    def __init__(self) -> None:
        self.capabilities: dict[str, ActionCapability] = {}
        self.plans: dict[str, Plan] = {}

    def register_capability(self, capability: ActionCapability) -> None:
        self.capabilities[capability.name] = capability

    def plan_for(self, goal: Goal) -> Plan:
        steps = [PlanStep("internal_reflection", "analisar o próximo passo do objetivo sem tocar no dispositivo", ActionRisk.NONE, False)]
        plan = Plan(goal.id, steps, confidence=0.55)
        self.plans[goal.id] = plan
        return plan

    def request_initiative(self, goal: Goal | None, context: str) -> Initiative | None:
        if goal is None:
            return None
        plan = self.plans.get(goal.id) or self.plan_for(goal)
        step = plan.steps[0]
        capability = self.capabilities.get(step.action)
        if capability is None or not capability.enabled or capability.permission == PermissionMode.DENY:
            return None
        requires = step.requires_confirmation or capability.permission != PermissionMode.ALLOW or not capability.background_allowed
        return Initiative(reason=f"Objetivo ativo: {goal.title}. Contexto: {context}", goal_id=goal.id, action=step.action, requires_confirmation=requires)
