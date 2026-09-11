from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class RuntimeCommand(StrEnum):
    PERCEIVE = "perceive"
    THINK = "think"
    INTERNAL_CYCLE = "internal_cycle"
    SNAPSHOT = "snapshot"


@dataclass(frozen=True)
class RuntimeRequest:
    """Contrato neutro para o corpo Android falar com o núcleo local."""

    command: RuntimeCommand
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command.value,
            "payload": self.payload,
            "request_id": self.request_id,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class RuntimeResponse:
    """Resposta serializável; não pressupõe qualquer modelo de linguagem."""

    ok: bool
    payload: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    request_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "payload": self.payload,
            "error": self.error,
            "request_id": self.request_id,
        }


def encode_request(request: RuntimeRequest) -> str:
    import json

    return json.dumps(request.to_dict(), ensure_ascii=False, separators=(",", ":"))


def decode_request(raw: str) -> RuntimeRequest:
    import json

    data = json.loads(raw)
    return RuntimeRequest(
        command=RuntimeCommand(data["command"]),
        payload=dict(data.get("payload") or {}),
        request_id=str(data.get("request_id", "")),
        created_at=str(data.get("created_at", "")),
    )
