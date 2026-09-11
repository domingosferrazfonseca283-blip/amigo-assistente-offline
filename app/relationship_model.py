from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class UserProfile:
    """Representação probabilística do utilizador, sem confundir hipótese com facto."""

    name: str | None = None
    preferences: dict[str, Any] = field(default_factory=dict)
    interests: dict[str, float] = field(default_factory=dict)
    interaction_patterns: dict[str, float] = field(default_factory=dict)
    boundaries: set[str] = field(default_factory=set)
    confidence: float = 0.2
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def observe_preference(self, key: str, value: Any, confidence: float = 0.6) -> None:
        self.preferences[key] = {"value": value, "confidence": max(0.0, min(1.0, confidence))}
        self.confidence = min(0.99, self.confidence + 0.03)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def reinforce_interest(self, topic: str, amount: float = 0.08) -> None:
        key = topic.strip().lower()
        if not key:
            return
        self.interests[key] = min(1.0, self.interests.get(key, 0.0) + amount)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def describe(self) -> dict[str, Any]:
        data = asdict(self)
        data["boundaries"] = sorted(self.boundaries)
        return data


@dataclass
class RelationshipState:
    """Estado da relação ao longo do tempo; não representa emoções humanas reais."""

    interaction_count: int = 0
    continuity_score: float = 0.0
    trust_proxy: float = 0.5
    familiarity: float = 0.0
    shared_topics: dict[str, float] = field(default_factory=dict)
    important_moments: list[str] = field(default_factory=list)
    last_interaction: str | None = None

    def observe_interaction(self, topics: list[str] | None = None, important: bool = False, episode_id: str | None = None) -> None:
        self.interaction_count += 1
        self.familiarity = min(1.0, self.familiarity + 0.01)
        self.continuity_score = min(1.0, self.continuity_score * 0.995 + 0.02)
        self.last_interaction = datetime.now(timezone.utc).isoformat()
        for topic in topics or []:
            key = topic.strip().lower()
            if key:
                self.shared_topics[key] = min(1.0, self.shared_topics.get(key, 0.0) + 0.05)
        if important and episode_id:
            self.important_moments.append(episode_id)
            self.important_moments = self.important_moments[-100:]

    def describe(self) -> dict[str, Any]:
        return asdict(self)


class RelationshipModel:
    """Modelo persistente de quem participa na relação e de como ela evolui."""

    def __init__(self) -> None:
        self.user = UserProfile()
        self.relationship = RelationshipState()

    def observe(self, text: str, *, topics: list[str] | None = None, important: bool = False, episode_id: str | None = None) -> None:
        self.relationship.observe_interaction(topics, important, episode_id)
        for topic in topics or []:
            self.user.reinforce_interest(topic)
        self.user.confidence = min(0.99, self.user.confidence + 0.01)

    def snapshot(self) -> dict[str, Any]:
        return {"user": self.user.describe(), "relationship": self.relationship.describe()}

    def restore(self, snapshot: dict[str, Any] | None) -> None:
        if not snapshot:
            return
        user = dict(snapshot.get("user", {}))
        self.user = UserProfile(
            name=user.get("name"),
            preferences=dict(user.get("preferences", {})),
            interests={str(k): float(v) for k, v in dict(user.get("interests", {})).items()},
            interaction_patterns={str(k): float(v) for k, v in dict(user.get("interaction_patterns", {})).items()},
            boundaries=set(user.get("boundaries", [])),
            confidence=float(user.get("confidence", 0.2)),
            updated_at=str(user.get("updated_at", datetime.now(timezone.utc).isoformat())),
        )
        rel = dict(snapshot.get("relationship", {}))
        self.relationship = RelationshipState(
            interaction_count=int(rel.get("interaction_count", 0)),
            continuity_score=float(rel.get("continuity_score", 0.0)),
            trust_proxy=float(rel.get("trust_proxy", 0.5)),
            familiarity=float(rel.get("familiarity", 0.0)),
            shared_topics={str(k): float(v) for k, v in dict(rel.get("shared_topics", {})).items()},
            important_moments=list(rel.get("important_moments", [])),
            last_interaction=rel.get("last_interaction"),
        )
