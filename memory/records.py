from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryKind(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    RELATIONAL = "relational"
    PROCEDURAL = "procedural"
    REFLECTIVE = "reflective"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryRecord:
    content: str
    kind: MemoryKind = MemoryKind.EPISODIC
    importance: float = 0.5
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    last_accessed_at: str = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.importance = max(0.0, min(1.0, float(self.importance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "content": self.content,
            "importance": self.importance,
            "created_at": self.created_at,
            "last_accessed_at": self.last_accessed_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "MemoryRecord":
        import json

        record_id, kind, content, importance, created_at, last_accessed_at, metadata = row
        return cls(
            id=record_id,
            kind=MemoryKind(kind),
            content=content,
            importance=importance,
            created_at=created_at,
            last_accessed_at=last_accessed_at,
            metadata=json.loads(metadata) if metadata else {},
        )
