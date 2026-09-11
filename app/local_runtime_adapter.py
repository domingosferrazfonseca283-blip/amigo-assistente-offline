from __future__ import annotations

from typing import Any, Callable

from .cognitive_runtime import CognitiveRuntime
from .internal_cognitive_cycle import InternalCognitiveCycle
from .internal_life import InternalActivity
from .local_runtime_protocol import RuntimeCommand, RuntimeRequest, RuntimeResponse


class LocalRuntimeAdapter:
    """Adaptador executável entre o protocolo local e o núcleo cognitivo.

    Este componente não abre sockets, não usa HTTP e não acede à Internet.
    O hospedeiro fornece uma instância já construída de ``CognitiveRuntime``.
    """

    def __init__(self, runtime: CognitiveRuntime) -> None:
        self.runtime = runtime
        self.internal_cycle = InternalCognitiveCycle(runtime)
        self._handlers: dict[RuntimeCommand, Callable[[dict[str, Any]], dict[str, Any]]] = {
            RuntimeCommand.PERCEIVE: self._perceive,
            RuntimeCommand.THINK: self._think,
            RuntimeCommand.INTERNAL_CYCLE: self._internal_cycle,
            RuntimeCommand.SNAPSHOT: self._snapshot,
        }

    def dispatch(self, request: RuntimeRequest) -> RuntimeResponse:
        handler = self._handlers.get(request.command)
        if handler is None:
            return RuntimeResponse(False, error=f"Comando não suportado: {request.command.value}", request_id=request.request_id)
        try:
            return RuntimeResponse(True, payload=handler(request.payload), request_id=request.request_id)
        except Exception as exc:
            return RuntimeResponse(False, error=f"{type(exc).__name__}: {exc}", request_id=request.request_id)

    def _perceive(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise ValueError("PERCEIVE exige payload.text não vazio")
        self.runtime.perceive(text)
        return {"accepted": True, "text": text}

    def _think(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise ValueError("THINK exige payload.text não vazio")
        return {"text": self.runtime.think(text)}

    def _internal_cycle(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw_activity = str(payload.get("activity", InternalActivity.REFLECT.value))
        try:
            activity = InternalActivity(raw_activity)
        except ValueError as exc:
            raise ValueError(f"atividade interna inválida: {raw_activity}") from exc
        report = self.internal_cycle.run(activity)
        return {
            "activity": report.activity,
            "cycle_id": report.cycle_id,
            "completed_phases": report.completed_phases,
            "focus": report.focus,
            "expectations": report.expectations,
            "surprises": report.surprises,
            "unresolved_questions": report.unresolved_questions,
            "timestamp": report.timestamp,
        }

    def _snapshot(self, _payload: dict[str, Any]) -> dict[str, Any]:
        return self.runtime.snapshot()

    def handle_json(self, raw: str) -> str:
        from .local_runtime_protocol import decode_request, encode_request

        request = decode_request(raw)
        return encode_request(self.dispatch(request))
