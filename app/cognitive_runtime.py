from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .affect import AffectEngine
from .agency import ActionCapability, ActionRisk, AgencyEngine, PermissionMode
from .autonomy import AutonomyEngine, Choice
from .cognitive_events import CognitiveEvent, EventType
from .cognitive_state import NoemiaState
from .consolidation import OfflineConsolidator
from .decision_learning import DecisionLearner
from .episodic_memory import EpisodicMemory
from .event_bus import EventBus
from .expectation_engine import ExpectationEngine
from .global_workspace import GlobalWorkspace, WorkspaceKind
from .goals import GoalManager
from .initiative import InitiativeEngine, InitiativePolicy
from .memory import LocalMemory
from .memory_association import AssociativeMemory, MemoryNode
from .memory_context import MemoryContext
from .memory_retrieval import CognitiveMemoryRetriever
from .relationship_model import RelationshipModel
from .semantic_memory import SemanticMemory
from .self_model import SelfModel
from .state_change import ChangeDetectionEngine, StateHistory
from .temporal_memory import TemporalMemory, TemporalRelation
from .temporal_reasoning import TemporalReasoningEngine
from .world_model import WorldModel


class LocalModel(Protocol):
    def generate(self, prompt: str) -> str: ...


class LocalKnowledge(Protocol):
    def search(self, query: str, limit: int = 5) -> list[str]: ...


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
        self.associations = AssociativeMemory()
        self.memory_retriever = CognitiveMemoryRetriever(self.episodic, self.semantic, self.associations)
        self.relationship = RelationshipModel()
        self.timeline = TemporalMemory()
        self.temporal_reasoning = TemporalReasoningEngine()
        self.state_history = StateHistory()
        self.change_detector = ChangeDetectionEngine()
        self.expectations = ExpectationEngine()
        self.agency = AgencyEngine()
        self._register_internal_capabilities()
        self.initiative = InitiativeEngine(self.goals, self.agency, InitiativePolicy())
        self.autonomy = AutonomyEngine()
        self.decision_learning = DecisionLearner()
        self.consolidator = OfflineConsolidator(self.episodic, self.semantic, self.bus)
        self.workspace = GlobalWorkspace()
        self.bus.subscribe(EventType.USER_MESSAGE, self._handle_user_message)

    def _register_internal_capabilities(self) -> None:
        self.agency.register_capability(ActionCapability(
            "internal_reflection", "Preparar reflexão interna sem tocar no dispositivo.", ActionRisk.NONE, PermissionMode.ALLOW, True,
        ))
        self.agency.register_capability(ActionCapability(
            "store_memory", "Guardar memória local.", ActionRisk.LOW, PermissionMode.ALLOW, True,
        ))

    def perceive(self, text: str) -> None:
        self.workspace.clear_cycle()
        self.workspace.submit(text, WorkspaceKind.PERCEPTION, salience=0.9, confidence=0.98, source="user")
        self.bus.publish(CognitiveEvent(EventType.USER_MESSAGE, {"text": text}, source="user", importance=0.8))

    def _handle_user_message(self, event: CognitiveEvent) -> None:
        text = str(event.payload.get("text", "")).strip()
        if not text:
            return
        self.state.touch()
        self.state.turn_count += 1
        self.affect.on_input(text)
        topics = self._extract_topics(text)
        episode = self.episodic.record(
            "Interação recebida: " + text,
            {"event_id": event.id, "role": "user"},
            importance=event.importance,
            emotional_salience=self.state.affect.novelty,
            source="perception",
        )
        self.associations.add_node(MemoryNode(episode.id, "episode", episode.summary, episode.salience))
        self.timeline.record(episode.summary, source="perception", importance=event.importance, tags=topics, event_id=episode.id, timestamp=episode.timestamp)
        self.relationship.observe(text, topics=topics, important=event.importance >= 0.9, episode_id=episode.id)
        self.world.observe_user_statement(text, confidence=0.95)
        self.workspace.submit(episode.summary, WorkspaceKind.MEMORY, salience=episode.salience, confidence=0.85, source="episodic_memory")
        for goal in self.goals.active()[:6]:
            self.workspace.submit(f"{goal.title} (progresso={goal.progress:.2f})", WorkspaceKind.GOAL, salience=goal.priority, confidence=0.95, source="goal_manager")
        self.state.working_memory.append({"type": "user", "text": text, "event_id": event.id})
        self.state.working_memory = self.state.working_memory[-24:]

    @staticmethod
    def _extract_topics(text: str) -> list[str]:
        words = [word.strip(".,!?;:()[]{}\"'").lower() for word in text.split()]
        stop = {"sobre", "quero", "tenho", "estou", "porque", "quando", "também", "muito", "para", "como", "mais", "menos", "essa", "esse", "isso", "ainda", "vamos"}
        return list(dict.fromkeys(word for word in words if len(word) >= 5 and word not in stop))[:8]

    def create_goal(self, title: str, priority: float = 0.5, source: str = "user"):
        goal = self.goals.add(title, priority, source)
        self.state.active_goals = [g.id for g in self.goals.active()]
        self.workspace.submit(f"{goal.title} (progresso={goal.progress:.2f})", WorkspaceKind.GOAL, salience=goal.priority, confidence=0.95, source="goal_manager")
        self.bus.publish(CognitiveEvent(EventType.GOAL_CREATED, {"id": goal.id, "title": goal.title, "priority": goal.priority}, source="goal_manager", importance=0.8))
        self.agency.plan_for(goal)
        return goal

    def maybe_create_internal_goal(self, title: str, priority: float = 0.7):
        if not self.autonomy.should_create_goal(priority):
            return None
        return self.create_goal(title, priority, source="autonomy")

    def _choose_goal(self):
        active = self.goals.active()
        if not active:
            return None, None
        choices = [Choice(g.id, max(0.0, min(1.0, g.priority * 0.8 + (1.0 - g.progress) * 0.2)), [f"prioridade={g.priority:.2f}", f"progresso={g.progress:.2f}"]) for g in active[:8]]
        for choice in choices:
            choice.score = self.decision_learning.score("priorização de objetivos", choice.option, choice.score)
        decision = self.autonomy.choose("priorização de objetivos", choices)
        chosen = next((g for g in active if decision.chosen and g.id == decision.chosen.option), None)
        if decision.chosen:
            self.workspace.submit(f"Escolha: {decision.chosen.option}", WorkspaceKind.GOAL, salience=decision.chosen.score, confidence=decision.chosen.score, source="autonomy")
        return chosen or active[0], decision

    def evaluate_initiative(self, context: str = "inatividade"):
        goal, decision = self._choose_goal()
        if goal is None:
            return None
        initiative = self.agency.request_initiative(goal, context)
        if initiative is not None:
            self.initiative.pending.append(initiative)
            self.initiative.pending = self.initiative.pending[-self.initiative.policy.max_pending:]
            self.workspace.submit(f"Iniciativa: {initiative.action}", WorkspaceKind.POSSIBILITY, salience=0.75, confidence=0.7, source="initiative")
            self.bus.publish(CognitiveEvent(EventType.ACTION_REQUESTED, {"action": initiative.action, "goal_id": initiative.goal_id, "requires_confirmation": initiative.requires_confirmation, "reason": initiative.reason, "decision_id": decision.id if decision else None}, source="initiative", importance=0.75))
        return initiative

    def approve_initiative(self, index: int = 0):
        return self.initiative.approve(index)

    def expect_state(self, subject: str, predicate: str, expected: object, confidence: float = 0.5, source: str = "prediction", evidence: list[str] | None = None):
        expectation = self.expectations.expect(subject, predicate, expected, confidence, source, evidence=evidence)
        self.workspace.submit(f"Expectativa: {subject}.{predicate} = {expected}", WorkspaceKind.EXPECTATION, salience=confidence, confidence=confidence, source="expectation")
        return expectation

    def run_consolidation(self):
        report = self.consolidator.run()
        from .memory_consolidation import MemoryConsolidator
        graph_report = MemoryConsolidator().consolidate(self.episodic, self.semantic, self.associations)
        temporal_report = self.temporal_reasoning.analyze(self.episodic, self.relationship, self.timeline)
        for change in self.state_history.recent_changes(limit=20):
            self.timeline.relate(change.evidence[0] if change.evidence else change.id, change.id, TemporalRelation.CHANGES, change.confidence, change.evidence)
        self.workspace.submit("Consolidação da memória e aprendizagem", WorkspaceKind.SELF_SIGNAL, salience=0.65, confidence=0.9, source="consolidation")
        self.state.reflections.append(
            f"Consolidação: {report.reflections} reflexões, {report.adjusted_beliefs} ajustes; rede: {graph_report.nodes_created} nós, {graph_report.links_created} ligações; padrões: {graph_report.patterns_found}; tempo: {temporal_report.events_linked} ligações, {temporal_report.repetitions_found} repetições, {temporal_report.possible_changes} mudanças possíveis; histórico: {len(self.state_history.changes)} mudanças; decisões aprendidas: {len(self.decision_learning.outcomes)}; expectativas: {len(self.expectations.results)} resultados"
        )
        self.state.reflections = self.state.reflections[-100:]
        self.bus.publish(CognitiveEvent(EventType.CONSOLIDATION, {"memory": report.__dict__, "graph": graph_report.__dict__, "temporal": temporal_report.__dict__, "changes": len(self.state_history.changes), "decisions": len(self.decision_learning.outcomes), "expectations": len(self.expectations.results)}, source="consolidation", importance=0.6))
        return report

    def learn_user_fact(self, subject: str, predicate: str, value: object):
        belief = self.semantic.learn_user_fact(subject, predicate, value)
        episode = self.episodic.record(
            f"Facto fornecido pelo utilizador: {subject} {predicate} {value}",
            {"subject": subject, "predicate": predicate, "value": value}, importance=0.9, source="user_fact",
        )
        self.timeline.record(episode.summary, source="user_fact", importance=0.9, tags=[subject, predicate], event_id=episode.id, timestamp=episode.timestamp)
        self.workspace.submit(episode.summary, WorkspaceKind.MEMORY, salience=0.9, confidence=belief.confidence, source="user_fact")
        change = self.change_detector.ingest_belief(self.state_history, subject=subject, predicate=predicate, value=value, confidence=belief.confidence, source="user_fact", evidence=[belief.id, episode.id])
        expectation_result = self.expectations.observe(subject, predicate, value, evidence=[belief.id, episode.id], confidence=belief.confidence)
        if expectation_result is not None:
            self.workspace.submit(
                f"Surpresa={expectation_result.surprise:.2f}: esperado={expectation_result.expected}, observado={expectation_result.observed}",
                WorkspaceKind.EXPECTATION,
                salience=max(0.35, expectation_result.surprise),
                confidence=expectation_result.confidence,
                source="expectation",
            )
            self.bus.publish(CognitiveEvent(EventType.REFLECTION, {"expectation_id": expectation_result.expectation_id, "expected": expectation_result.expected, "observed": expectation_result.observed, "surprise": expectation_result.surprise, "matched": expectation_result.matched, "status": expectation_result.status.value}, source="expectation", importance=max(0.3, expectation_result.surprise)))
        if change is not None:
            self.timeline.relate(change.evidence[0], episode.id, TemporalRelation.CHANGES, change.confidence, change.evidence)
            self.bus.publish(CognitiveEvent(EventType.WORLD_UPDATED, {"subject": subject, "property": predicate, "old": change.old_value, "new": change.new_value, "change_id": change.id, "permanence": change.permanence.value}, source="state_history", importance=0.85))
        return belief

    def think(self, user_text: str) -> str:
        self.workspace.clear_cycle()
        self.expectations.expire()
        self.workspace.submit(user_text, WorkspaceKind.PERCEPTION, salience=0.9, confidence=0.98, source="user")
        context = self._retrieve_context(user_text)
        goal, decision = self._choose_goal()
        initiative = self.agency.request_initiative(goal, "durante interação") if goal else None
        if initiative:
            self.workspace.submit(f"Proposta: {initiative.action}", WorkspaceKind.POSSIBILITY, salience=0.7, confidence=0.7, source="initiative")
        self.workspace.compete(
            curiosity=self.state.affect.curiosity,
            uncertainty=self.state.affect.uncertainty,
            novelty=self.state.affect.novelty,
        )
        context["workspace"] = self.workspace.active_context()
        prompt = self._compose_context(user_text, context, goal.title if goal else None, initiative.action if initiative else None)
        self.bus.publish(CognitiveEvent(EventType.DECISION, {"goal": goal.title if goal else None, "initiative": initiative.action if initiative else None, "decision_id": decision.id if decision else None, "focus": self.workspace.active_context()}, source="runtime"))
        try:
            response = self.model.generate(prompt).strip()
        except Exception as exc:
            self.affect.on_failure()
            self.episodic.record("Falha durante geração local", {"success": False, "error": type(exc).__name__, "input": user_text}, importance=0.7, source="runtime")
            if decision and decision.chosen:
                self.decision_learning.record_outcome(decision.id, decision.goal, decision.chosen.option, decision.chosen.score, -0.5, False)
            self.bus.publish(CognitiveEvent(EventType.EXPERIENCE, {"success": False, "error": type(exc).__name__}, source="runtime"))
            raise
        if not response:
            response = "Estou aqui. Vamos continuar."
        self.affect.on_success()
        self.memory.add("user", user_text)
        self.memory.add("assistant", response)
        response_episode = self.episodic.record("Resposta e experiência de interação", {"input": user_text, "output": response, "success": True}, importance=0.65, emotional_salience=self.state.affect.novelty, source="runtime")
        self.timeline.record(response_episode.summary, source="runtime", importance=0.65, tags=self._extract_topics(user_text), event_id=response_episode.id, timestamp=response_episode.timestamp)
        self.state.working_memory.append({"type": "assistant", "text": response})
        self.state.working_memory = self.state.working_memory[-24:]
        if decision and decision.chosen:
            self.decision_learning.record_outcome(decision.id, decision.goal, decision.chosen.option, decision.chosen.score, 0.25, True, [response_episode.id])
        self.workspace.submit("Resposta produzida e experiência registada", WorkspaceKind.SELF_SIGNAL, salience=0.65, confidence=0.9, source="runtime")
        self.bus.publish(CognitiveEvent(EventType.MODEL_RESPONSE, {"text": response}, source="local_model", importance=0.7))
        self.bus.publish(CognitiveEvent(EventType.EXPERIENCE, {"success": True, "input": user_text, "output": response, "focus": self.workspace.active_context()}, source="runtime"))
        return response

    def _retrieve_context(self, query: str) -> dict[str, list[str]]:
        memories = self.memory.recent(limit=16)
        matches = self.memory_retriever.retrieve(query, MemoryContext(topics=self._extract_topics(query)), limit=10)
        episodes = [f"{m.item.summary}" for m in matches if m.kind == "episode"]
        beliefs = [f"{m.item.subject} | {m.item.predicate} | {m.item.value} (confiança={m.item.confidence:.2f})" for m in matches if m.kind == "belief"]
        world = [f"{f.subject} | {f.predicate} | {f.value} (confiança={f.confidence:.2f})" for f in self.world.relevant(query)]
        knowledge: list[str] = []
        if self.knowledge is not None:
            try: knowledge = self.knowledge.search(query, limit=8)
            except Exception: knowledge = []
        relationship = [f"familiaridade={self.relationship.relationship.familiarity:.2f}", f"continuidade={self.relationship.relationship.continuity_score:.2f}", "tópicos partilhados=" + ", ".join(sorted(self.relationship.relationship.shared_topics, key=self.relationship.relationship.shared_topics.get, reverse=True)[:8])]
        temporal = [f"{item.timestamp}: {item.summary}" for item in self.timeline.recent(8)]
        changes = [f"{c.subject}.{c.property}: {c.old_value} → {c.new_value} ({c.permanence.value}, confiança={c.confidence:.2f})" for c in self.state_history.recent_changes(8)]
        decisions = [f"{o.goal} → {o.option}: recompensa={o.reward:.2f}, sucesso={o.success}" for o in self.decision_learning.recent(8)]
        expectations = [f"{e.subject}.{e.property} → {e.expected} (confiança={e.confidence:.2f}, fonte={e.source})" for e in self.expectations.active(8)]
        surprise = [f"esperado={r.expected} | observado={r.observed} | surpresa={r.surprise:.2f} | {r.status.value}" for r in self.expectations.recent_results(8)]
        return {"memory": [f"{m['role']}: {m['content']}" for m in memories], "episodes": episodes, "beliefs": beliefs, "world": world, "knowledge": knowledge, "relationship": relationship, "temporal": temporal, "changes": changes, "decisions": decisions, "expectations": expectations, "surprise": surprise, "workspace": []}

    def _compose_context(self, user_text: str, context: dict[str, list[str]], goal: str | None, initiative: str | None = None) -> str:
        return "\n".join([
            "IDENTIDADE OPERACIONAL:", f"Nome: {self.self_model.name}", f"Relação: {self.self_model.relationship}", "Estado interno operacional: " + str(self.state.affect.__dict__),
            "\nFOCO COGNITIVO GLOBAL:\n" + "\n".join(context.get("workspace", [])),
            "\nMODELO DA RELAÇÃO:\n" + "\n".join(context["relationship"]), "\nOBJETIVO ATIVO: " + (goal or "nenhum"), "\nINICIATIVA PROPOSTA: " + (initiative or "nenhuma"),
            "\nMEMÓRIA RECENTE:\n" + "\n".join(context["memory"]), "\nMEMÓRIA ASSOCIATIVA/EPISÓDICA:\n" + "\n".join(context["episodes"]),
            "\nCRENÇAS/FACTOS CONSOLIDADOS:\n" + "\n".join(context["beliefs"]), "\nMODELO DO MUNDO:\n" + "\n".join(context["world"]),
            "\nLINHA TEMPORAL RECENTE:\n" + "\n".join(context["temporal"]), "\nMUDANÇAS DE ESTADO:\n" + "\n".join(context["changes"]),
            "\nEXPECTATIVAS LOCAIS:\n" + "\n".join(context["expectations"]), "\nSURPRESAS RECENTES:\n" + "\n".join(context["surprise"]),
            "\nDECISÕES E CONSEQUÊNCIAS:\n" + "\n".join(context["decisions"]), "\nCONHECIMENTO LOCAL:\n" + "\n".join(f"- {x}" for x in context["knowledge"]), "\nENTRADA ATUAL:\n" + user_text,
            "\nResponda como Noémia: mantenha continuidade; diferencie facto, memória, inferência e hipótese. Expectativas são previsões locais, não certezas. Surpresa mede apenas divergência entre previsão e observação. Pode escolher entre objetivos e propostas internas, mas nunca invente capacidades, não execute ação externa sem permissão e não trate uma proposta como ação executada.",
        ])

    def snapshot(self) -> dict:
        return {
            "state": self.state.to_dict(), "self": self.self_model.describe(), "world": self.world.to_dict(), "relationship": self.relationship.snapshot(),
            "goals": [g.__dict__.copy() for g in self.goals.goals.values()], "episodic_memory": self.episodic.to_dict(), "semantic_memory": self.semantic.to_dict(),
            "associative_memory": self.associations.snapshot(), "temporal_memory": self.timeline.snapshot(), "state_history": self.state_history.snapshot(),
            "plans": {goal_id: {"goal_id": plan.goal_id, "confidence": plan.confidence, "steps": [step.__dict__.copy() for step in plan.steps]} for goal_id, plan in self.agency.plans.items()},
            "initiative": {"enabled": self.initiative.policy.enabled, "pending": [item.__dict__.copy() for item in self.initiative.pending]},
            "capabilities": {name: capability.__dict__.copy() for name, capability in self.agency.capabilities.items()},
            "autonomy": self.autonomy.snapshot(), "decision_learning": self.decision_learning.snapshot(),
            "expectations": self.expectations.snapshot(), "global_workspace": self.workspace.snapshot(),
        }
