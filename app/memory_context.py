from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class MemoryContext:
    """Contexto temporal e situacional associado a uma memória."""

    session_id: str | None = None
    location: str | None = None
    activity: str | None = None
    people: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: str | None = None
    tags: set[str] = field(default_factory=set)

    def score(self, query: str, current: "MemoryContext | None" = None) -> float:
        score = 0.0
        q = query.lower()
        fields = [self.location, self.activity, *self.people, *self.topics, *self.tags]
        score += sum(0.15 for value in fields if value and str(value).lower() in q)
        if current is not None:
            if self.location and current.location and self.location == current.location:
                score += 0.30
            if self.activity and current.activity and self.activity == current.activity:
                score += 0.25
            if set(self.people).intersection(current.people):
                score += 0.20
            if set(self.topics).intersection(current.topics):
                score += 0.15
        return min(1.0, score)


@dataclass
class ContextualMemory:
    memory_id: str
    context: MemoryContext
    valid_from: str
    valid_until: str | None = None
    active: bool = True
    id: str = field(default_factory=lambda: uuid4().hex)

    def is_valid(self, now: datetime | None = None) -> bool:
        if not self.active:
            return False
        now = now or datetime.now(timezone.utc)
        start = datetime.fromisoformat(self.valid_from)
        if now < start:
            return False
        if self.valid_until is not None and now > datetime.fromisoformat(self.valid_until):
            return False
        return True

    def deactivate(self) -> None:
        self.active = False
