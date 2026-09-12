from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from core.entity import Entity
from nervous_system import Event


class ReasoningModel(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass
class ThoughtContext:
    input_text: str
    memories: list[str] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)


@dataclass
class ThoughtResult:
    interpretation: str
    decision: str
    response: str | None = None
    confidence: float = 0.0
    action: str = "none"
    action_payload: Any = None


class Mind:
    """Camada cognitiva: percebe, interpreta, decide e propõe ações."""

    def __init__(self, entity: Entity, model: ReasoningModel | None = None) -> None:
        self.entity = entity
        self.model = model

    def perceive(self, text: str, *, events: list[Event] | None = None) -> ThoughtContext:
        normalized = text.strip()
        memories = [record.content for record in self.entity.recall(normalized, limit=8)] if normalized else []
        return ThoughtContext(input_text=normalized, memories=memories, events=events or [])

    def interpret(self, context: ThoughtContext) -> str:
        if not context.input_text and not context.events:
            return "nenhuma entrada significativa"
        if any(event.type.startswith("vision.") for event in context.events):
            return "entrada visual recebida do ambiente através do sistema nervoso"
        if any(event.type.startswith("speech.") for event in context.events):
            return "fala recebida do ambiente e convertida em texto"
        if any(event.type.startswith("hearing.") for event in context.events):
            return "atividade acústica recebida através da audição"
        if context.events:
            return "entrada recebida do ambiente através do sistema nervoso"
        if context.memories:
            return "entrada do utilizador relacionada com memória existente"
        return "nova entrada do utilizador que requer compreensão"

    def decide(self, context: ThoughtContext, interpretation: str) -> ThoughtResult:
        if self.model is None:
            return ThoughtResult(
                interpretation=interpretation,
                decision="aguardar um modelo de raciocínio",
                confidence=0.0,
            )

        prompt = self._build_prompt(context, interpretation)
        response = self.model.generate(prompt).strip()
        if context.input_text:
            self.entity.remember(
                context.input_text,
                metadata={"source": "mind", "role": "user"},
            )
        for event in context.events:
            if event.type in {"speech.final", "vision.interpretation"}:
                content = str(event.data.get("text") or event.data.get("description") or "").strip()
                if content:
                    self.entity.remember(content, metadata={"source": "perception", "event": event.type})
        if response:
            self.entity.remember(
                response,
                metadata={"source": "mind", "role": "noemia"},
            )
        return ThoughtResult(
            interpretation=interpretation,
            decision="responder ao utilizador" if response else "processar perceção",
            response=response,
            confidence=0.8 if response else 0.0,
            action="speak" if response else "none",
            action_payload=response or None,
        )

    def think(self, text: str, *, events: list[Event] | None = None) -> ThoughtResult:
        context = self.perceive(text, events=events)
        interpretation = self.interpret(context)
        return self.decide(context, interpretation)

    @staticmethod
    def _build_prompt(context: ThoughtContext, interpretation: str) -> str:
        memories = "\n".join(f"- {item}" for item in context.memories) or "- nenhuma"
        events = "\n".join(f"- {event.type}: {event.data}" for event in context.events) or "- nenhum"
        return (
            "Você é a mente de Noémia, uma entidade artificial persistente.\n"
            "Responda naturalmente e nunca invente memórias, capacidades ou perceções.\n"
            "Interpretação funcional: {interpretation}\n"
            "Memórias recuperadas:\n{memories}\n"
            "Eventos do ambiente:\n{events}\n"
            "Entrada: {input_text}\n"
        ).format(
            interpretation=interpretation,
            memories=memories,
            events=events,
            input_text=context.input_text,
        )
