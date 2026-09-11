from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .cognitive_cycle import CognitiveCycle, CognitiveCycleInput, CognitivePhase, CognitiveWorkspace
from .cognitive_events import CognitiveEvent, EventType
from .internal_life import InternalActivity, InternalCycleResult
from .predictive_cognition import PredictiveCognition


@dataclass
class InternalCognitionReport:
    activity: str
    cycle_id: str
    completed_phases: list[str]
    focus: list[str] = field(default_factory=list)
    expectations: list[str] = field(default_factory=list)
    surprises: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class InternalCognitiveCycle:
    """Executa um ciclo cognitivo de baixa carga sem depender de nova fala.

    O ciclo trabalha sobre estado já existente: atenção, objetivos, expectativas,
    previsões e memórias. Não concede capacidades externas nem cria consciência.
    """

    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self.cycle = CognitiveCycle()
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.cycle.register(CognitivePhase.OBSERVE, self._observe)
        self.cycle.register(CognitivePhase.RECALL, self._recall)
        self.cycle.register(CognitivePhase.INTERPRET, self._interpret)
        self.cycle.register(CognitivePhase.EVALUATE, self._evaluate)
        self.cycle.register(CognitivePhase.DELIBERATE, self._deliberate)
        self.cycle.register(CognitivePhase.LEARN, self._learn)

    def _observe(self, _input: CognitiveCycleInput, workspace: CognitiveWorkspace) -> str:
        workspace.focus.append("atividade interna")
        return "estado interno observado"

    def _recall(self, _input: CognitiveCycleInput, workspace: CognitiveWorkspace) -> list[str]:
        memories = self.runtime.memory.recent(limit=6)
        return [f"{item['role']}: {item['content']}" for item in memories]

    def _interpret(self, _input: CognitiveCycleInput, workspace: CognitiveWorkspace) -> list[str]:
        return [
            f"expectativas ativas={len(self.runtime.expectations.active(20))}",
            f"mudanças observadas={len(self.runtime.state_history.recent_changes(20))}",
        ]

    def _evaluate(self, _input: CognitiveCycleInput, workspace: CognitiveWorkspace) -> list[str]:
        top = self.runtime.goals.top()
        if top is None:
            return ["nenhum objetivo ativo"]
        return [f"objetivo prioritário: {top.title} ({top.priority:.2f})"]

    def _deliberate(self, _input: CognitiveCycleInput, workspace: CognitiveWorkspace) -> None:
        active = self.runtime.expectations.active(6)
        workspace.expectations.extend(
            f"{item.subject}.{item.property} → {item.expected} ({item.confidence:.2f})"
            for item in active
        )
        return None

    def _learn(self, _input: CognitiveCycleInput, workspace: CognitiveWorkspace) -> dict[str, list[str]]:
        questions: list[str] = []
        if workspace.surprises:
            questions.append("Reexaminar previsões que divergiram da observação.")
        return {"unresolved_questions": questions}

    def run(self, activity: InternalActivity = InternalActivity.REFLECT) -> InternalCognitionReport:
        cycle_input = CognitiveCycleInput(
            kind="internal",
            payload={"activity": activity.value},
            source="internal_life",
        )
        result = self.cycle.run(cycle_input)
        report = InternalCognitionReport(
            activity=activity.value,
            cycle_id=result.cycle_id,
            completed_phases=[phase.value for phase in result.completed_phases],
            focus=list(result.workspace.focus),
            expectations=list(result.workspace.expectations),
            surprises=list(result.workspace.surprises),
            unresolved_questions=list(result.workspace.unresolved_questions),
        )
        self.runtime.bus.publish(
            CognitiveEvent(
                EventType.REFLECTION,
                {"activity": activity.value, "cycle_id": result.cycle_id, "completed_phases": report.completed_phases, "expectations": report.expectations, "questions": report.unresolved_questions},
                source="internal_cognitive_cycle",
                importance=0.5,
            )
        )
        return report
