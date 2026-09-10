from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class EventType(StrEnum):
    OBSERVATION = "observation"
    USER_MESSAGE = "user_message"
    MODEL_RESPONSE = "model_response"
    MEMORY_RECALLED = "memory_recalled"
    WORLD_UPDATED = "world_updated"
    GOAL_CREATED = "goal_created"
    GOAL_UPDATED = "goal_updated"
    DECISION = "decision"
    ACTION_REQUESTED = "action_requested"
    EXPERIENCE = "experience"
    REFLECTION = "reflection"
    CONSOLIDATION = "consolidation"
    SYSTEM = "system"


@dataclass(slots=True)
class CognitiveEvent:
    type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "core"
    importance: float = 0.5
    privacy_scope: str = "local"
    id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
            "source": self.source,
            "importance": self.importance,
            "privacy_scope": self.privacy_scope,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CognitiveEvent":
        return cls(
            id=str(data["id"]),
            type=EventType(data["type"]),
            payload=dict(data.get("payload", {})),
            source=str(data.get("source", "core")),
            importance=float(data.get("importance", 0.5)),
            privacy_scope=str(data.get("privacy_scope", "local")),
            timestamp=str(data.get("timestamp", datetime.now(timezone.utc).isoformat())),
        )
