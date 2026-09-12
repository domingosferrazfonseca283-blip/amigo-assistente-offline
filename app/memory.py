from __future__ import annotations

from typing import Any

from memory import MemoryKind, MemorySystem


class LocalMemory:
    """Adaptador de compatibilidade para a memória persistente da entidade.

    O armazenamento real é o MemorySystem/SQLite. Esta classe mantém a API
    antiga da camada de aplicação sem criar uma segunda memória concorrente.
    """

    def __init__(self, memory: MemorySystem | None = None) -> None:
        self.memory = memory or MemorySystem.local()

    def add(self, role: str, content: str) -> None:
        self.memory.remember(
            content,
            kind=MemoryKind.EPISODIC,
            metadata={"role": role},
        )

    def recent(self, limit: int = 12) -> list[dict[str, Any]]:
        records = self.memory.recent(limit=limit, kind=MemoryKind.EPISODIC)
        return [
            {
                "role": str(record.metadata.get("role", "unknown")),
                "content": record.content,
                "id": record.id,
                "created_at": record.created_at,
            }
            for record in reversed(records)
        ]
