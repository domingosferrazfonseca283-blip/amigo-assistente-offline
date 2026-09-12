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


class Mind:
    """Camada cognitiva da entidade: percebe, interpreta e decide."""

    def __init__(self, entity: Entity, model: ReasoningModel | None = None) -> None:
        self.entity = entity
        self.model = model

    def perceive(self, text: str, *, events: list[Event] | None = None) -> ThoughtContext:
        memories = [record.content for record in self.entity.recall(text, limit=8)]
        return ThoughtContext(input_text=text, memories=memories, events=events or [])

    def interpret(self, context: ThoughtContext) -> str:
        if not context.input_text.strip():
            return "nenhuma entrada significativa"
        if context.memories:
            return "entrada do utilizador relacionada com memória existente"
        return "nova entrada do utilizador que requer compreensão"

    def decide(self, context: ThoughtContext, interpretation: str) -> ThoughtResult:
        if self.model is None:
            return ThoughtResult(
                interpretation=interpretation,
                decision="responder ao utilizador",
                confidence=0.2,
            )

        prompt = self._build_prompt(context, interpretation)
        response = self.model.generate(prompt).strip()
        self.entity.remember(
            context.input_text,
            metadata={"source": "mind", "role": "user"},
        )
        if response:
            self.entity.remember(
                response,
                metadata={"source": "mind", "role": "noemia"},
            )
        return ThoughtResult(
            interpretation=interpretation,
            decision="responder ao utilizador",
            response=response,
            confidence=0.8,
        )

    def think(self, text: str, *, events: list[Event] | None = None) -> ThoughtResult:
        context = self.perceive(text, events=events)
        interpretation = self.interpret(context)
        return self.decide(context, interpretation)

    @staticmethod
    def _build_prompt(context: ThoughtContext, interpretation: str) -> str:
        memories = "\n".join(f"- {item}" for item in context.memories) or "- nenhuma"
        return (
            "Você é a mente de Noémia. Responda naturalmente ao utilizador.\n"
            "Interpretação funcional: {interpretation}\n"
            "Memórias recuperadas:\n{memories}\n"
            "Entrada: {input_text}\n"
            "Não invente memórias nem capacidades."
        ).format(
            interpretation=interpretation,
            memories=memories,
            input_text=context.input_text,
        )
