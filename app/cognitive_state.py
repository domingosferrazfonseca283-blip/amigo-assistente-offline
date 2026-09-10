from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from typing import Any
from uuid import uuid4


@dataclass
class AffectState:
    curiosity: float = 0.45
    confidence: float = 0.60
    uncertainty: float = 0.25
    cognitive_load: float = 0.10
    novelty: float = 0.20
    priority: float = 0.50

    def clamp(self) -> None:
        for name in self.__dataclass_fields__:
            setattr(self, name, max(0.0, min(1.0, float(getattr(self, name)))))


@dataclass
class NoemiaState:
    version: int = 1
    session_id: str = field(default_factory=lambda: uuid4().hex)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    turn_count: int = 0
    affect: AffectState = field(default_factory=AffectState)
    active_goals: list[str] = field(default_factory=list)
    working_memory: list[dict[str, Any]] = field(default_factory=list)
    pending_events: list[dict[str, Any]] = field(default_factory=list)
    reflections: list[str] = field(default_factory=list)
    self_state: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NoemiaState":
        affect = AffectState(**dict(data.get("affect", {})))
        return cls(
            version=int(data.get("version", 1)),
            session_id=str(data.get("session_id", uuid4().hex)),
            started_at=str(data.get("started_at", datetime.now(timezone.utc).isoformat())),
            last_activity=str(data.get("last_activity", datetime.now(timezone.utc).isoformat())),
            turn_count=int(data.get("turn_count", 0)),
            affect=affect,
            active_goals=list(data.get("active_goals", [])),
            working_memory=list(data.get("working_memory", [])),
            pending_events=list(data.get("pending_events", [])),
            reflections=list(data.get("reflections", [])),
            self_state=dict(data.get("self_state", {})),
        )
