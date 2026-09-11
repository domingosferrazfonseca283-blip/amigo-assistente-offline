from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class PatternKind(StrEnum):
    STABLE = "stable"
    CYCLE = "cycle"
    REVERSAL = "reversal"
    TREND = "trend"


@dataclass
class PatternObservation:
    subject: str
    property: str
    kind: PatternKind
    sequence: list[str]
    confidence: float
    evidence: list[str] = field(default_factory=list)
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


class PatternMemory:
    """Memória de padrões: conserva sequências observadas sem convertê-las em leis."""

    def __init__(self, max_patterns: int = 5000) -> None:
        self.max_patterns = max_patterns
        self.patterns: list[PatternObservation] = []

    def add(self, subject: str, property: str, kind: PatternKind, sequence: list[str], confidence: float, evidence: list[str] | None = None) -> PatternObservation:
        pattern = PatternObservation(subject, property, kind, sequence[-12:], max(0.0, min(1.0, confidence)), evidence or [])
        self.patterns.append(pattern)
        if len(self.patterns) > self.max_patterns:
            self.patterns = self.patterns[-self.max_patterns:]
        return pattern

    def relevant(self, subject: str | None = None, property: str | None = None, limit: int = 20) -> list[PatternObservation]:
        items = [p for p in self.patterns if (subject is None or p.subject == subject) and (property is None or p.property == property)]
        return sorted(items, key=lambda p: p.confidence, reverse=True)[:limit]

    def snapshot(self) -> dict:
        return {"patterns": [asdict(p) | {"kind": p.kind.value} for p in self.patterns]}


class PatternDetector:
    """Deteta estabilidade, ciclos, reversões e tendências em históricos de estado."""

    @staticmethod
    def _values(history, subject: str, property: str, limit: int = 20):
        return history.history(subject, property, limit=limit)

    def detect(self, history, patterns: PatternMemory, *, subject: str, property: str) -> list[PatternObservation]:
        snapshots = self._values(history, subject, property)
        if len(snapshots) < 2:
            return []
        values = [str(item.value) for item in snapshots]
        evidence = [item.id for item in snapshots[-8:]]
        found: list[PatternObservation] = []

        if len(set(values[-3:])) == 1 and len(values) >= 3:
            found.append(patterns.add(subject, property, PatternKind.STABLE, values[-3:], 0.78, evidence))

        if len(values) >= 4 and values[-4] == values[-2] and values[-3] == values[-1] and values[-4] != values[-3]:
            found.append(patterns.add(subject, property, PatternKind.CYCLE, values[-4:], 0.82, evidence))

        if len(values) >= 3 and values[-1] == values[-3] and values[-1] != values[-2]:
            found.append(patterns.add(subject, property, PatternKind.REVERSAL, values[-3:], 0.76, evidence))

        if len(values) >= 3 and all(values[i] != values[i - 1] for i in range(1, len(values[-3:]))):
            found.append(patterns.add(subject, property, PatternKind.TREND, values[-3:], 0.55, evidence))

        return found
