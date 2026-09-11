from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class Permanence(StrEnum):
    UNKNOWN = "unknown"
    TEMPORARY = "temporary"
    PERSISTENT = "persistent"


@dataclass
class StateSnapshot:
    subject: str
    property: str
    value: Any
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "observation"
    confidence: float = 0.5
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class StateChange:
    subject: str
    property: str
    old_value: Any
    new_value: Any
    changed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "observation"
    confidence: float = 0.5
    permanence: Permanence = Permanence.UNKNOWN
    evidence: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)


class StateHistory:
    """Histórico de estados: distingue valor atual, mudança e grau de permanência."""

    def __init__(self, max_snapshots: int = 10000, max_changes: int = 5000) -> None:
        self.max_snapshots = max_snapshots
        self.max_changes = max_changes
        self.snapshots: list[StateSnapshot] = []
        self.changes: list[StateChange] = []
        self._current: dict[tuple[str, str], StateSnapshot] = {}

    @staticmethod
    def _same_value(left: Any, right: Any) -> bool:
        return left == right and type(left) is type(right)

    def observe(self, subject: str, property: str, value: Any, *, source: str = "observation", confidence: float = 0.5, evidence: list[str] | None = None) -> StateChange | None:
        snapshot = StateSnapshot(subject, property, value, source=source, confidence=max(0.0, min(1.0, confidence)))
        key = (subject, property)
        previous = self._current.get(key)
        self.snapshots.append(snapshot)
        self._current[key] = snapshot
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots:]
        if previous is None or self._same_value(previous.value, value):
            return None
        change = StateChange(subject, property, previous.value, value, source=source, confidence=min(previous.confidence, snapshot.confidence), evidence=evidence or [previous.id, snapshot.id])
        self.changes.append(change)
        if len(self.changes) > self.max_changes:
            self.changes = self.changes[-self.max_changes:]
        return change

    def current(self, subject: str, property: str) -> StateSnapshot | None:
        return self._current.get((subject, property))

    def history(self, subject: str | None = None, property: str | None = None, limit: int = 50) -> list[StateSnapshot]:
        items = [s for s in self.snapshots if (subject is None or s.subject == subject) and (property is None or s.property == property)]
        return items[-limit:]

    def recent_changes(self, limit: int = 50) -> list[StateChange]:
        return self.changes[-limit:]

    def mark_permanence(self, change_id: str, permanence: Permanence) -> StateChange | None:
        for change in reversed(self.changes):
            if change.id == change_id:
                change.permanence = permanence
                return change
        return None

    def snapshot(self) -> dict[str, Any]:
        return {
            "snapshots": [asdict(item) for item in self.snapshots],
            "changes": [asdict(item) | {"permanence": item.permanence.value} for item in self.changes],
        }


class ChangeDetectionEngine:
    """Deteta mudanças observáveis sem assumir causalidade ou permanência."""

    def ingest_belief(self, history: StateHistory, *, subject: str, predicate: str, value: Any, confidence: float, source: str, evidence: list[str] | None = None) -> StateChange | None:
        return history.observe(subject, predicate, value, source=source, confidence=confidence, evidence=evidence)

    def classify(self, history: StateHistory, change: StateChange, *, repeat_threshold: int = 3) -> StateChange:
        later = [s for s in history.history(change.subject, change.property, limit=20) if s.timestamp > change.changed_at]
        if len(later) >= repeat_threshold and later[-1].value == change.new_value:
            change.permanence = Permanence.PERSISTENT
        elif any(s.value == change.old_value for s in later):
            change.permanence = Permanence.TEMPORARY
        return change
