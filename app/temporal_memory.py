from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class TemporalRelation(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    FOLLOWS = "follows"
    CAUSES_POSSIBLY = "possibly_causes"
    CHANGES = "changes"
    REPEATS = "repeats"


@dataclass
class TimelineEvent:
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "experience"
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class TemporalLink:
    source: str
    target: str
    relation: TemporalRelation
    confidence: float = 0.5
    evidence: list[str] = field(default_factory=list)


class TemporalMemory:
    """Linha temporal local para ligar acontecimentos, mudanças e padrões."""

    def __init__(self, max_events: int = 10000) -> None:
        self.max_events = max_events
        self.events: list[TimelineEvent] = []
        self.links: list[TemporalLink] = []

    def record(self, summary: str, *, source: str = "experience", importance: float = 0.5, tags: list[str] | None = None, event_id: str | None = None, timestamp: str | None = None) -> TimelineEvent:
        event = TimelineEvent(summary, timestamp=timestamp or datetime.now(timezone.utc).isoformat(), source=source, importance=max(0.0, min(1.0, importance)), tags=tags or [], id=event_id or uuid4().hex)
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        return event

    def relate(self, source: str, target: str, relation: TemporalRelation, confidence: float = 0.5, evidence: list[str] | None = None) -> TemporalLink:
        existing = next((link for link in self.links if link.source == source and link.target == target and link.relation == relation), None)
        if existing:
            existing.confidence = max(existing.confidence, confidence)
            existing.evidence = list(dict.fromkeys(existing.evidence + (evidence or [])))[-20:]
            return existing
        link = TemporalLink(source, target, relation, max(0.0, min(1.0, confidence)), evidence or [])
        self.links.append(link)
        return link

    def recent(self, limit: int = 20) -> list[TimelineEvent]:
        return self.events[-limit:]

    def related(self, event_id: str, limit: int = 20) -> list[TemporalLink]:
        links = [link for link in self.links if link.source == event_id or link.target == event_id]
        return links[-limit:]

    def snapshot(self) -> dict[str, Any]:
        return {"events": [asdict(event) for event in self.events], "links": [asdict(link) | {"relation": link.relation.value} for link in self.links]}
