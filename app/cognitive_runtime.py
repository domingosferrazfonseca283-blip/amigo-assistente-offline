from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .affect import AffectEngine
from .agency import ActionCapability, ActionRisk, AgencyEngine, PermissionMode
from .cognitive_events import CognitiveEvent, EventType
from .cognitive_state import NoemiaState
from .consolidation import OfflineConsolidator
from .episodic_memory import EpisodicMemory
from .event_bus import EventBus
from .goals import GoalManager
from .initiative import InitiativeEngine, InitiativePolicy
from .memory import LocalMemory
from .semantic_memory import SemanticMemory
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
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.agency = AgencyEngine()
        self._register_internal_capabilities()
        self.initiative = InitiativeEngine(self.goals, self.agency, InitiativePolicy())
        self.consolidator = OfflineConsolidator(self.episodic, self.semantic, self.bus)
        self.bus.subscribe(EventType.USER_MESSAGE, self._handle_user_message)

    def _register_internal_capabilities(self) -> None:
        self.agency.register_capability(ActionCapability(
            "internal_reflection",
            "Preparar reflexão interna sem tocar no dispositivo.",
            ActionRisk.NONE,
            PermissionMode.ALLOW,
            background_allowed=True,
        ))
        self.agency.register_capability(ActionCapability(
            "store_memory",
            "Guardar memória local.",
            ActionRisk.LOW,
            PermissionMode.ALLOW,
            background_allowed=True,
        ))

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
        self.episodic.record(
            "Interação recebida: " + text,
            {"event_id": event.id, "role": "user"},
            importance=event.importance,
            emotional_salience=self.state.affect.novelty,
            source="perception",
        )
        self.state.working_memory.append({"type": "user", "text": text, "event_id": event.id})
        self.state.working_memory = self.state.working_memory[-24:]

    def create_goal(self, title: str, priority: float = 0.5, source: str = "user"):
        goal = self.goals.add(title, priority, source)
        self.state.active_goals = [g.id for g in self.goals.active()]
        self.bus.publish(CognitiveEvent(EventType.GOAL_CREATED, {
            "id": goal.id, "title": goal.title, "priority": goal.priority,
        }, source="goal_manager", importance=0.8))
        self.agency.plan_for(goal)
        return goal

    def evaluate_initiative(self, context: str = "inatividade"):
        initiative = self.initiative.evaluate(context)
        if initiative is not None:
            self.bus.publish(CognitiveEvent(EventType.ACTION_REQUESTED, {
                "action": initiative.action,
                "goal_id": initiative.goal_id,
                "requires_confirmation": initiative.requires_confirmation,
                "reason": initiative.reason,
            }, source="initiative", importance=0.75))
        return initiative

    def approve_initiative(self, index: int = 0):
        return self.initiative.approve(index)

    def run_consolidation(self):
        report = self.consolidator.run()
        self.state.reflections.extend(
            f"Consolidação: {report.reflections} reflexões, {report.adjusted_beliefs} ajustes"
            for _ in range(1)
        )
        self.state.reflections = self.state.reflections[-100:]
        return report

    def learn_user_fact(self, subject: str, predicate: str, value: object):
        belief = self.semantic.learn_user_fact(subject, predicate, value)
        self.episodic.record(
            f"Facto fornecido pelo utilizador: {subject} {predicate} {value}",
            {"subject": subject, "predicate": predicate, "value": value},
            importance=0.9,
            source="user_fact",
        )
        return belief

    def think(self, user_text: str) -> str:
        """Executa percepção, recuperação, agência e geração local num ciclo único."""
        context = self._retrieve_context(user_text)
        goal = self.goals.top()
        initiative = self.evaluate_initiative("durante interação") if goal else None
        prompt = self._compose_context(
            user_text,
            context,
            goal.title if goal else None,
            initiative.action if initiative else None,
        )
        self.bus.publish(CognitiveEvent(EventType.DECISION, {
            "goal": goal.title if goal else None,
            "initiative": initiative.action if initiative else None,
        }, source="runtime"))
        try:
            response = self.model.generate(prompt).strip()
        except Exception as exc:
            self.affect.on_failure()
            self.episodic.record(
                "Falha durante geração local",
                {"success": False, "error": type(exc).__name__, "input": user_text},
                importance=0.7,
                source="runtime",
            )
            self.bus.publish(CognitiveEvent(EventType.EXPERIENCE, {
                "success": False, "error": type(exc).__name__,
            }, source="runtime"))
            raise
        if not response:
            response = "Estou aqui. Vamos continuar."
        self.affect.on_success()
        self.memory.add("user", user_text)
        self.memory.add("assistant", response)
        self.episodic.record(
            "Resposta e experiência de interação",
            {"input": user_text, "output": response, "success": True},
            importance=0.65,
            emotional_salience=self.state.affect.novelty,
            source="runtime",
        )
        self.state.working_memory.append({"type": "assistant", "text": response})
        self.state.working_memory = self.state.working_memory[-24:]
        self.bus.publish(CognitiveEvent(EventType.MODEL_RESPONSE, {"text": response}, source="local_model", importance=0.7))
        self.bus.publish(CognitiveEvent(EventType.EXPERIENCE, {
            "success": True, "input": user_text, "output": response,
        }, source="runtime"))
        return response

    def _retrieve_context(self, query: str) -> dict[str, list[str]]:
        memories = self.memory.recent(limit=16)
        episodes = [
            f"{e.summary} (saliencia={e.salience:.2f})"
            for e in self.episodic.recall(query, limit=8)
        ]
        beliefs = [
            f"{b.subject} | {b.predicate} | {b.value} (confiança={b.confidence:.2f}, tipo={b.kind.value})"
            for b in self.semantic.search(query, limit=8)
        ]
        world = [
            f"{f.subject} | {f.predicate} | {f.value} (confiança={f.confidence:.2f})"
            for f in self.world.relevant(query)
        ]
        knowledge: list[str] = []
        if self.knowledge is not None:
            try:
                knowledge = self.knowledge.search(query, limit=8)
            except Exception:
                knowledge = []
        return {
            "memory": [f"{m['role']}: {m['content']}" for m in memories],
            "episodes": episodes,
            "beliefs": beliefs,
            "world": world,
            "knowledge": knowledge,
        }

    def _compose_context(
        self,
        user_text: str,
        context: dict[str, list[str]],
        goal: str | None,
        initiative: str | None = None,
    ) -> str:
        parts = [
            "IDENTIDADE OPERACIONAL:",
            f"Nome: {self.self_model.name}",
            f"Relação: {self.self_model.relationship}",
            "Estado interno operacional: " + str(self.state.affect.__dict__),
            "\nOBJETIVO ATIVO: " + (goal or "nenhum"),
            "\nINICIATIVA PROPOSTA: " + (initiative or "nenhuma"),
            "\nMEMÓRIA RECENTE:\n" + "\n".join(context["memory"]),
            "\nMEMÓRIA EPISÓDICA:\n" + "\n".join(context["episodes"]),
            "\nCRENÇAS/FACTOS CONSOLIDADOS:\n" + "\n".join(context["beliefs"]),
            "\nMODELO DO MUNDO:\n" + "\n".join(context["world"]),
            "\nCONHECIMENTO LOCAL:\n" + "\n".join(f"- {x}" for x in context["knowledge"]),
            "\nENTRADA ATUAL:\n" + user_text,
            "\nResponda como Noémia: mantenha continuidade, diferencie facto, memória, inferência e hipótese. Nunca invente memória nem trate uma proposta de ação como ação executada.",
        ]
        return "\n".join(parts)

    def snapshot(self) -> dict:
        return {
            "state": self.state.to_dict(),
            "self": self.self_model.describe(),
            "world": self.world.to_dict(),
            "goals": [g.__dict__.copy() for g in self.goals.goals.values()],
            "episodic_memory": self.episodic.to_dict(),
            "semantic_memory": self.semantic.to_dict(),
            "plans": {
                goal_id: {
                    "goal_id": plan.goal_id,
                    "confidence": plan.confidence,
                    "steps": [step.__dict__.copy() for step in plan.steps],
                }
                for goal_id, plan in self.agency.plans.items()
            },
            "initiative": {
                "enabled": self.initiative.policy.enabled,
                "pending": [item.__dict__.copy() for item in self.initiative.pending],
            },
            "capabilities": {
                name: capability.__dict__.copy()
                for name, capability in self.agency.capabilities.items()
            },
        }
