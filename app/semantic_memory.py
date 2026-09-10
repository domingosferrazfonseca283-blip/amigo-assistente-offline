from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class BeliefKind(StrEnum):
    USER_FACT = "user_fact"
    OBSERVED = "observed"
    INFERRED = "inferred"
    HYPOTHESIS = "hypothesis"
    LOCAL_SOURCE = "local_source"


@dataclass
class Belief:
    subject: str
    predicate: str
    value: Any
    kind: BeliefKind
    confidence: float = 0.5
    source: str = "internal"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


class SemanticMemory:
    def __init__(self) -> None:
        self.beliefs: dict[str, Belief] = {}

    def upsert(self, belief: Belief) -> Belief:
        self.beliefs[belief.id] = belief
        return belief

    def learn_user_fact(self, subject: str, predicate: str, value: Any) -> Belief:
        return self.upsert(Belief(subject, predicate, value, BeliefKind.USER_FACT, 0.95, "user"))

    def search(self, query: str, limit: int = 8) -> list[Belief]:
        terms = set(query.lower().split())
        scored: list[tuple[float, Belief]] = []
        for belief in self.beliefs.values():
            text = f"{belief.subject} {belief.predicate} {belief.value}".lower()
            overlap = sum(term in text for term in terms)
            if overlap:
                scored.append((overlap + belief.confidence * 0.25, belief))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [belief for _, belief in scored[:limit]]

    def contradictions(self, belief: Belief) -> list[Belief]:
        return [
            other for other in self.beliefs.values()
            if other.id != belief.id
            and other.subject == belief.subject
            and other.predicate == belief.predicate
            and other.value != belief.value
            and other.confidence >= 0.5
        ]

    def to_dict(self) -> list[dict[str, Any]]:
        return [asdict(b) | {"kind": b.kind.value} for b in self.beliefs.values()]
