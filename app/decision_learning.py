from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class DecisionOutcome:
    decision_id: str
    goal: str
    option: str
    expected_score: float
    reward: float
    success: bool
    evidence: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class LearnedPreference:
    key: str
    option: str
    weight: float = 0.0
    confidence: float = 0.0
    observations: int = 0
    last_reward: float = 0.0


class DecisionLearner:
    """Aprende com consequências observadas sem transformar uma escolha isolada em regra."""

    def __init__(self, max_outcomes: int = 2000) -> None:
        self.max_outcomes = max_outcomes
        self.outcomes: list[DecisionOutcome] = []
        self.preferences: dict[str, LearnedPreference] = {}

    def record_outcome(self, decision_id: str, goal: str, option: str, expected_score: float, reward: float, success: bool, evidence: list[str] | None = None) -> DecisionOutcome:
        outcome = DecisionOutcome(decision_id, goal, option, max(0.0, min(1.0, expected_score)), max(-1.0, min(1.0, reward)), success, evidence or [])
        self.outcomes.append(outcome)
        self.outcomes = self.outcomes[-self.max_outcomes:]
        self._learn(goal, option, outcome.reward)
        return outcome

    def _learn(self, goal: str, option: str, reward: float) -> None:
        key = f"{goal}::{option}"
        pref = self.preferences.get(key)
        if pref is None:
            pref = LearnedPreference(key=goal, option=option)
            self.preferences[key] = pref
        pref.observations += 1
        alpha = 1.0 / min(pref.observations, 20)
        pref.weight += alpha * (reward - pref.weight)
        pref.last_reward = reward
        pref.confidence = min(0.95, 0.15 + 0.05 * pref.observations)

    def score(self, goal: str, option: str, base_score: float) -> float:
        pref = self.preferences.get(f"{goal}::{option}")
        if pref is None:
            return base_score
        learned = (pref.weight + 1.0) / 2.0
        return max(0.0, min(1.0, base_score * 0.75 + learned * 0.25 * pref.confidence))

    def recent(self, limit: int = 20) -> list[DecisionOutcome]:
        return self.outcomes[-limit:][::-1]

    def snapshot(self) -> dict[str, Any]:
        return {"outcomes": [asdict(item) for item in self.outcomes[-self.max_outcomes:]], "preferences": [asdict(item) for item in self.preferences.values()]}
