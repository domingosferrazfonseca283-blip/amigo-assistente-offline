from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .agency import ActionCapability, PermissionMode


class ActionHandler(Protocol):
    def execute(self, action: str, payload: dict[str, Any]) -> Any:
        ...


@dataclass
class ActionRequest:
    action: str
    payload: dict[str, Any]
    confirmed: bool = False


class ActionSystem:
    def __init__(self) -> None:
        self.capabilities: dict[str, ActionCapability] = {}
        self.handlers: dict[str, ActionHandler] = {}

    def register(self, capability: ActionCapability, handler: ActionHandler) -> None:
        self.capabilities[capability.name] = capability
        self.handlers[capability.name] = handler

    def execute(self, request: ActionRequest) -> Any:
        capability = self.capabilities.get(request.action)
        handler = self.handlers.get(request.action)
        if capability is None or handler is None or not capability.enabled:
            raise PermissionError(f"Ação não disponível: {request.action}")
        if capability.permission == PermissionMode.DENY:
            raise PermissionError(f"Ação bloqueada pela política: {request.action}")
        if capability.permission == PermissionMode.CONFIRM and not request.confirmed:
            raise PermissionError(f"Confirmação necessária: {request.action}")
        return handler.execute(request.action, request.payload)
