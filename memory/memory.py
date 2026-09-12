from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .records import MemoryKind, MemoryRecord
from .store import MemoryStore


@dataclass
class MemorySystem:
    """Interface de alto nível para memória de longo prazo da entidade."""

    store: MemoryStore

    @classmethod
    def local(cls, path: str = "data/entity_memory.sqlite3") -> "MemorySystem":
        return cls(MemoryStore(path))

    def remember(
        self,
        content: str,
        *,
        kind: MemoryKind = MemoryKind.EPISODIC,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        if not content.strip():
            raise ValueError("Uma memória não pode ter conteúdo vazio.")
        return self.store.add(
            MemoryRecord(
                content=content.strip(),
                kind=kind,
                importance=importance,
                metadata=metadata or {},
            )
        )

    def recall(self, query: str, limit: int = 10, kind: MemoryKind | None = None) -> list[MemoryRecord]:
        return self.store.search(query, limit=limit, kind=kind)

    def recent(self, limit: int = 10, kind: MemoryKind | None = None) -> list[MemoryRecord]:
        return self.store.recent(limit=limit, kind=kind)

    def remember_episode(self, content: str, importance: float = 0.5, **metadata: Any) -> MemoryRecord:
        return self.remember(content, kind=MemoryKind.EPISODIC, importance=importance, metadata=metadata)

    def remember_fact(self, content: str, importance: float = 0.7, **metadata: Any) -> MemoryRecord:
        return self.remember(content, kind=MemoryKind.SEMANTIC, importance=importance, metadata=metadata)

    def remember_relationship(self, content: str, importance: float = 0.8, **metadata: Any) -> MemoryRecord:
        return self.remember(content, kind=MemoryKind.RELATIONAL, importance=importance, metadata=metadata)

    def remember_procedure(self, content: str, importance: float = 0.7, **metadata: Any) -> MemoryRecord:
        return self.remember(content, kind=MemoryKind.PROCEDURAL, importance=importance, metadata=metadata)

    def remember_reflection(self, content: str, importance: float = 0.6, **metadata: Any) -> MemoryRecord:
        return self.remember(content, kind=MemoryKind.REFLECTIVE, importance=importance, metadata=metadata)

    def snapshot(self) -> list[dict[str, object]]:
        return self.store.export_records()

    def restore(self, records: list[dict[str, object]]) -> int:
        return self.store.import_records(records)
