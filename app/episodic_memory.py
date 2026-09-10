from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class Episode:
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    emotional_salience: float = 0.0
    source: str = "experience"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)
    access_count: int = 0

    @property
    def salience(self) -> float:
        return max(0.0, min(1.0, 0.6 * self.importance + 0.4 * self.emotional_salience))


class EpisodicMemory:
    def __init__(self, capacity: int = 10000) -> None:
        self.capacity = capacity
        self.episodes: list[Episode] = []

    def record(self, summary: str, details: dict[str, Any] | None = None, *, importance: float = 0.5, emotional_salience: float = 0.0, source: str = "experience") -> Episode:
        episode = Episode(summary, details or {}, importance, emotional_salience, source)
        self.episodes.append(episode)
        if len(self.episodes) > self.capacity:
            self.episodes.sort(key=lambda e: (e.salience, e.timestamp), reverse=True)
            self.episodes = self.episodes[: self.capacity]
        return episode

    def recall(self, query: str, limit: int = 8) -> list[Episode]:
        terms = set(query.lower().split())
        scored: list[tuple[float, Episode]] = []
        for episode in self.episodes:
            haystack = f"{episode.summary} {episode.details}".lower()
            overlap = sum(1 for term in terms if term in haystack)
            score = overlap + episode.salience * 0.35
            if overlap or episode.salience >= 0.8:
                scored.append((score, episode))
        scored.sort(key=lambda item: item[0], reverse=True)
        result = [episode for _, episode in scored[:limit]]
        for episode in result:
            episode.access_count += 1
        return result

    def to_dict(self) -> list[dict[str, Any]]:
        return [asdict(e) for e in self.episodes]
