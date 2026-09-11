from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from .state_change import StateChange, StateHistory


class DynamicPattern(StrEnum):
    STABLE = "stable"
    REVERSAL = "reversal"
    OSCILLATION = "oscillation"
    REPEATED_CHANGE = "repeated_change"
    TEMPORARY = "temporary"


@dataclass
class StatePattern:
    subject: str
    property: str
    pattern: DynamicPattern
    confidence: float
    values: list[Any] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


class StateDynamicsEngine:
    """Reconhece dinâmica de estados sem confundir repetição com causalidade."""

    def analyze(self, history: StateHistory, *, limit: int = 500) -> list[StatePattern]:
        grouped: dict[tuple[str, str], list] = {}
        for snapshot in history.snapshots[-limit:]:
            grouped.setdefault((snapshot.subject, snapshot.property), []).append(snapshot)

        patterns: list[StatePattern] = []
        for (subject, property), snapshots in grouped.items():
            values = [item.value for item in snapshots]
            if len(values) < 2:
                continue
            changes = [change for change in history.changes if change.subject == subject and change.property == property]
            if not changes:
                patterns.append(StatePattern(subject, property, DynamicPattern.STABLE, 0.65, values[-3:], [snapshots[-1].id]))
                continue

            transitions = [(change.old_value, change.new_value) for change in changes[-12:]]
            latest = transitions[-1]
            reversal = any(old == latest[1] and new == latest[0] for old, new in transitions[:-1])
            unique_values = []
            for value in values:
                if value not in unique_values:
                    unique_values.append(value)

            if reversal and len(unique_values) == 2:
                pattern = DynamicPattern.OSCILLATION if len(transitions) >= 3 else DynamicPattern.REVERSAL
                confidence = min(0.9, 0.55 + 0.08 * len(transitions))
            elif len(transitions) >= 3:
                pattern = DynamicPattern.REPEATED_CHANGE
                confidence = min(0.85, 0.50 + 0.06 * len(transitions))
            else:
                pattern = DynamicPattern.TEMPORARY if any(change.permanence.value == "temporary" for change in changes[-3:]) else DynamicPattern.REPEATED_CHANGE
                confidence = 0.55

            evidence = [item.id for item in changes[-6:]]
            patterns.append(StatePattern(subject, property, pattern, confidence, values[-8:], evidence))
        return patterns

    @staticmethod
    def summarize(patterns: list[StatePattern]) -> list[str]:
        return [
            f"{pattern.subject}.{pattern.property}: {pattern.pattern.value} (confiança={pattern.confidence:.2f})"
            for pattern in patterns
        ]
