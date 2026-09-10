from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LocalMemory:
    """Memória simples e persistente em JSON, totalmente local."""

    def __init__(self, path: str | Path = "memory/memory.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.items: list[dict[str, Any]] = self._load()

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def add(self, role: str, content: str) -> None:
        self.items.append({"role": role, "content": content})
        self.save()

    def recent(self, limit: int = 12) -> list[dict[str, Any]]:
        return self.items[-limit:]

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
