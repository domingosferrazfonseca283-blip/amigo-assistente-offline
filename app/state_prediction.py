from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .state_change import StateHistory
from .state_dynamics import DynamicPattern, StateDynamicsEngine


@dataclass
class StatePrediction:
    subject: str
    property: str
    predicted_value: Any
    confidence: float
    basis: str
    evidence: list[str] = field(default_factory=list)


class LocalStatePredictor:
    """Previsão local conservadora baseada apenas em sequências já observadas."""

    def predict(self, history: StateHistory, *, subject: str, property: str) -> StatePrediction | None:
        snapshots = history.history(subject, property, limit=20)
        if len(snapshots) < 3:
            return None
        values = [item.value for item in snapshots]
        transitions = [(values[i - 1], values[i]) for i in range(1, len(values))]
        latest = values[-1]
        previous = values[-2]
        evidence = [item.id for item in snapshots[-6:]]

        if latest == previous:
            return StatePrediction(subject, property, latest, 0.72, "estado estável observado", evidence)

        reverse_count = sum(1 for old, new in transitions[:-1] if old == latest and new == previous)
        if reverse_count >= 1:
            return StatePrediction(subject, property, previous, min(0.78, 0.58 + 0.08 * reverse_count), "reversão observada anteriormente", evidence)

        if transitions[-2:] and transitions[-1] == transitions[-2]:
            return StatePrediction(subject, property, latest, 0.62, "transição repetida", evidence)

        patterns = StateDynamicsEngine().analyze(history)
        pattern = next((p for p in patterns if p.subject == subject and p.property == property), None)
        if pattern and pattern.pattern in {DynamicPattern.STABLE, DynamicPattern.REPEATED_CHANGE}:
            return StatePrediction(subject, property, latest, min(0.60, pattern.confidence), "padrão recente sem direção previsível", evidence)
        return None
