from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .affect import AffectEngine
from .cognitive_events import CognitiveEvent, EventType
from .cognitive_state import NoemiaState
from .event_bus import EventBus
from .goals import GoalManager
from .memory import LocalMemory
from .self_model import SelfModel
from .world_model import WorldModel


class LocalModel(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class LocalKnowledge(Protocol):
    def search(self, query: str, limit: int = 5) -> list[str]:
        ...


@dataclass
class CognitiveRuntime:
    model: LocalModel
    memory: LocalMemory
    knowledge: LocalKnowledge | None = None
    state: NoemiaState = field(default_factory=NoemiaState)
    world: WorldModel = field(default_factory=WorldModel)
    self_model: SelfModel = field(default_factory=SelfModel)
    goals: GoalManager = field(default_factory=GoalManager)
    bus: EventBus = field(default_factory=EventBus)

    def __post_init__(self) -> None:
        self.affect = AffectEngine(self.state.affect)
        self.bus.subscribe(EventType.USER_MESSAGE, self._handle_user_message)

    def perceive(self, text: str) -> None:
        self.bus.publish(CognitiveEvent(EventType.USER_MESSAGE, {"text": text}, source="user", importance=0.8))

    def _handle_user_message(self, event: CognitiveEvent) -> None:
        text = str(event.payload.get("text", "")).strip()
        if not text:
            return
        self.state.touch()
        self.state.turn_count += 1
        self.affect.on_input(text)
        self.world.remember_user_statement(text)
        self.state.working_memory.append({"type": "user", "text": text, "event_id": event.id})
        self.state.working_memory = self.state.working_memory[-24:]

    def think(self, user_text: str) -> str:
        """Executa um ciclo cognitivo completo antes de pedir a geração local."""
        context = self._retrieve_context(user_text)
        goal = self.goals.top()
        prompt = self._compose_context(user_text, context, goal.title if goal else None)
        self.bus.publish(CognitiveEvent(EventType.DECISION, {"goal": goal.title if goal else None}, source="runtime"))
        try:
            response = self.model.generate(prompt).strip()
        except Exception as exc:
            self.affect.on_failure()
            self.bus.publish(CognitiveEvent(EventType.EXPERIENCE, {"success": False, "error": type(exc).__name__}, source="runtime"))
            raise
        if not response:
            response = "Estou aqui. Vamos continuar."
        self.affect.on_success()
        self.memory.add("user", user_text)
        self.memory.add("assistant", response)
        self.state.working_memory.append({"type": "assistant", "text": response})
        self.state.working_memory = self.state.working_memory[-24:]
        self.bus.publish(CognitiveEvent(EventType.MODEL_RESPONSE, {"text": response}, source="local_model", importance=0.7))
        self.bus.publish(CognitiveEvent(EventType.EXPERIENCE, {"success": True, "input": user_text, "output": response}, source="runtime"))
        return response

    def _retrieve_context(self, query: str) -> dict[str, list[str]]:
        memories = self.memory.recent(limit=16)
        world = [f"{f.subject} | {f.predicate} | {f.value} (confiança={f.confidence:.2f})" for f in self.world.relevant(query)]
        knowledge: list[str] = []
        if self.knowledge is not None:
            try:
                knowledge = self.knowledge.search(query, limit=8)
            except Exception:
                knowledge = []
        return {"memory": [f"{m['role']}: {m['content']}" for m in memories], "world": world, "knowledge": knowledge}

    def _compose_context(self, user_text: str, context: dict[str, list[str]], goal: str | None) -> str:
        parts = [
            "IDENTIDADE OPERACIONAL:",
            f"Nome: {self.self_model.name}",
            f"Relação: {self.self_model.relationship}",
            "Estado interno operacional: " + str(self.state.affect.__dict__),
            "\nOBJETIVO ATIVO: " + (goal or "nenhum"),
            "\nMEMÓRIA RECENTE:\n" + "\n".join(context["memory"]),
            "\nMODELO DO MUNDO:\n" + "\n".join(context["world"]),
            "\nCONHECIMENTO LOCAL:\n" + "\n".join(f"- {x}" for x in context["knowledge"]),
            "\nENTRADA ATUAL:\n" + user_text,
            "\nResponda como Noémia: mantenha continuidade, diferencie fato de hipótese e não invente memória.",
        ]
        return "\n".join(parts)

    def snapshot(self) -> dict:
        return {
            "state": self.state.to_dict(),
            "self": self.self_model.describe(),
            "world": self.world.to_dict(),
            "goals": [g.__dict__.copy() for g in self.goals.goals.values()],
        }
