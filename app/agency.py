from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
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
    """Transforma objetivos em planos, mas nunca concede permissões por conta própria."""

    def __init__(self) -> None:
        self.capabilities: dict[str, ActionCapability] = {}
        self.plans: dict[str, Plan] = {}

    def register_capability(self, capability: ActionCapability) -> None:
        self.capabilities[capability.name] = capability

    def plan_for(self, goal: Goal) -> Plan:
        # Planeamento inicial deliberadamente genérico: o planner local pode
        # ser substituído por um planeador mais sofisticado sem alterar a API.
        steps = [PlanStep(
            action=f"analisar_proximo_passo:{goal.title}",
            reason="avançar o objetivo ativo com o menor compromisso possível",
            risk=ActionRisk.NONE,
            requires_confirmation=False,
        )]
        plan = Plan(goal.id, steps, confidence=0.55)
        self.plans[goal.id] = plan
        return plan

    def request_initiative(self, goal: Goal | None, context: str) -> Initiative | None:
        if goal is None:
            return None
        plan = self.plans.get(goal.id) or self.plan_for(goal)
        step = plan.steps[0]
        capability = self.capabilities.get(step.action)
        if capability is not None and not capability.enabled:
            return None
        requires = step.requires_confirmation
        if capability is not None:
            requires = requires or capability.permission != PermissionMode.ALLOW
            if not capability.background_allowed:
                requires = True
        return Initiative(
            reason=f"Objetivo ativo: {goal.title}. Contexto: {context}",
            goal_id=goal.id,
            action=step.action,
            requires_confirmation=requires,
        )
