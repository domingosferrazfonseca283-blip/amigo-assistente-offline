from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .records import MemoryKind, MemoryRecord, utc_now


class MemoryStore:
    """Armazém SQLite local para memória durável e pesquisável."""

    def __init__(self, path: str | Path = "data/entity_memory.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")

    def add(self, record: MemoryRecord) -> MemoryRecord:
        with self._connect() as db:
            db.execute(
                """INSERT OR REPLACE INTO memories
                   (id, kind, content, importance, created_at, last_accessed_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.id,
                    record.kind.value,
                    record.content,
                    record.importance,
                    record.created_at,
                    record.last_accessed_at,
                    json.dumps(record.metadata, ensure_ascii=False),
                ),
            )
        return record

    def get(self, record_id: str) -> MemoryRecord | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT id, kind, content, importance, created_at, last_accessed_at, metadata FROM memories WHERE id = ?",
                (record_id,),
            ).fetchone()
        if row is None:
            return None
        record = MemoryRecord.from_row(tuple(row))
        self.touch(record.id)
        record.last_accessed_at = utc_now()
        return record

    def recent(self, limit: int = 20, kind: MemoryKind | None = None) -> list[MemoryRecord]:
        limit = max(1, int(limit))
        sql = "SELECT id, kind, content, importance, created_at, last_accessed_at, metadata FROM memories"
        params: list[object] = []
        if kind is not None:
            sql += " WHERE kind = ?"
            params.append(kind.value)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as db:
            rows = db.execute(sql, params).fetchall()
        return [MemoryRecord.from_row(tuple(row)) for row in rows]

    def search(self, query: str, limit: int = 20, kind: MemoryKind | None = None) -> list[MemoryRecord]:
        terms = [term.strip().lower() for term in query.split() if term.strip()]
        if not terms:
            return self.recent(limit=limit, kind=kind)

        clauses = ["LOWER(content) LIKE ?" for _ in terms]
        sql = "SELECT id, kind, content, importance, created_at, last_accessed_at, metadata FROM memories WHERE "
        sql += " AND ".join(clauses)
        params: list[object] = [f"%{term}%" for term in terms]
        if kind is not None:
            sql += " AND kind = ?"
            params.append(kind.value)
        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(max(1, int(limit)))
        with self._connect() as db:
            rows = db.execute(sql, params).fetchall()
        return [MemoryRecord.from_row(tuple(row)) for row in rows]

    def touch(self, record_id: str) -> None:
        with self._connect() as db:
            db.execute("UPDATE memories SET last_accessed_at = ? WHERE id = ?", (utc_now(), record_id))

    def delete(self, record_id: str) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM memories WHERE id = ?", (record_id,))

    def count(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM memories").fetchone()[0])

    def export_records(self) -> list[dict[str, object]]:
        return [record.to_dict() for record in self.recent(limit=10_000)]

    def import_records(self, records: Iterable[dict[str, object]]) -> int:
        imported = 0
        for item in records:
            record = MemoryRecord(
                id=str(item["id"]),
                kind=MemoryKind(str(item["kind"])),
                content=str(item["content"]),
                importance=float(item.get("importance", 0.5)),
                created_at=str(item.get("created_at", utc_now())),
                last_accessed_at=str(item.get("last_accessed_at", utc_now())),
                metadata=dict(item.get("metadata", {})),
            )
            self.add(record)
            imported += 1
        return imported
