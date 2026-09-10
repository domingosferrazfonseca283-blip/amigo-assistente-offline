from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class WorldFact:
    subject: str
    predicate: str
    value: Any
    confidence: float = 0.7
    source: str = "inference"
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_until: str | None = None


class WorldModel:
    """Modelo local do que Noémia considera verdadeiro sobre o seu contexto."""

    def __init__(self) -> None:
        self._facts: list[WorldFact] = []

    def observe(self, fact: WorldFact) -> None:
        self._facts.append(fact)

    def remember_user_statement(self, statement: str, confidence: float = 0.95) -> None:
        self.observe(WorldFact("user", "stated", statement, confidence, "user"))

    def query(self, subject: str | None = None, predicate: str | None = None) -> list[WorldFact]:
        return [
            f for f in self._facts
            if (subject is None or f.subject == subject)
            and (predicate is None or f.predicate == predicate)
        ]

    def relevant(self, query: str, limit: int = 8) -> list[WorldFact]:
        terms = set(query.lower().split())
        scored: list[tuple[float, WorldFact]] = []
        for fact in self._facts:
            text = f"{fact.subject} {fact.predicate} {fact.value}".lower()
            overlap = len(terms.intersection(text.split()))
            if overlap:
                scored.append((overlap * fact.confidence, fact))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [fact for _, fact in scored[:limit]]

    def to_dict(self) -> list[dict[str, Any]]:
        return [fact.__dict__.copy() for fact in self._facts]

    @classmethod
    def from_dict(cls, data: list[dict[str, Any]]) -> "WorldModel":
        model = cls()
        for item in data:
            model.observe(WorldFact(**item))
        return model
