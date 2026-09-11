from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable
from uuid import uuid4


class CognitivePhase(StrEnum):
    OBSERVE = "observe"
    UPDATE_STATE = "update_state"
    RECALL = "recall"
    INTERPRET = "interpret"
    IMAGINE = "imagine"
    EVALUATE = "evaluate"
    DELIBERATE = "deliberate"
    CHOOSE = "choose"
    ACT = "act"
    EXPERIENCE = "experience"
    LEARN = "learn"
    CONSOLIDATE = "consolidate"


@dataclass
class CognitiveCycleInput:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "runtime"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class CognitiveWorkspace:
    """Espaço cognitivo global: o pequeno conjunto de coisas que está ativo agora."""

    focus: list[str] = field(default_factory=list)
    memories: list[str] = field(default_factory=list)
    world_hypotheses: list[str] = field(default_factory=list)
    self_signals: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    possibilities: list[str] = field(default_factory=list)
    selected_option: str | None = None
    unresolved_questions: list[str] = field(default_factory=list)
    expectations: list[str] = field(default_factory=list)
    surprises: list[str] = field(default_factory=list)

    def clear_transient(self) -> None:
        self.memories.clear()
        self.world_hypotheses.clear()
        self.possibilities.clear()
        self.selected_option = None
        self.unresolved_questions.clear()
        self.surprises.clear()


@dataclass
class CognitiveCycleResult:
    cycle_id: str
    input_id: str
    completed_phases: list[CognitivePhase]
    workspace: CognitiveWorkspace
    output: Any = None
    stopped_at: CognitivePhase | None = None
    error: str | None = None


class CognitiveCycle:
    """Orquestra a mente como um ciclo recorrente, não como uma cadeia de comandos.

    Cada fase é opcional e substituível. O núcleo mantém a ordem cognitiva e o
    workspace global, enquanto os módulos concretos fornecem a implementação.
    """

    ORDER = (
        CognitivePhase.OBSERVE,
        CognitivePhase.UPDATE_STATE,
        CognitivePhase.RECALL,
        CognitivePhase.INTERPRET,
        CognitivePhase.IMAGINE,
        CognitivePhase.EVALUATE,
        CognitivePhase.DELIBERATE,
        CognitivePhase.CHOOSE,
        CognitivePhase.ACT,
        CognitivePhase.EXPERIENCE,
        CognitivePhase.LEARN,
        CognitivePhase.CONSOLIDATE,
    )

    def __init__(self) -> None:
        self.workspace = CognitiveWorkspace()
        self.handlers: dict[CognitivePhase, Callable[[CognitiveCycleInput, CognitiveWorkspace], Any]] = {}
        self.history: list[CognitiveCycleResult] = []
        self.max_history = 1000

    def register(self, phase: CognitivePhase, handler: Callable[[CognitiveCycleInput, CognitiveWorkspace], Any]) -> None:
        self.handlers[phase] = handler

    def run(
        self,
        cycle_input: CognitiveCycleInput,
        *,
        phases: tuple[CognitivePhase, ...] | None = None,
        reset_transient: bool = True,
    ) -> CognitiveCycleResult:
        if reset_transient:
            self.workspace.clear_transient()

        selected_phases = phases or self.ORDER
        completed: list[CognitivePhase] = []
        result = CognitiveCycleResult(cycle_input.id, cycle_input.id, completed, self.workspace)

        for phase in selected_phases:
            handler = self.handlers.get(phase)
            if handler is None:
                continue
            try:
                output = handler(cycle_input, self.workspace)
                if output is not None:
                    self._merge_output(phase, output)
                completed.append(phase)
            except Exception as exc:
                result.stopped_at = phase
                result.error = type(exc).__name__
                break

        result.output = self.workspace.selected_option
        self.history.append(result)
        self.history = self.history[-self.max_history :]
        return result

    def _merge_output(self, phase: CognitivePhase, output: Any) -> None:
        if phase == CognitivePhase.RECALL:
            self.workspace.memories.extend(self._strings(output))
        elif phase == CognitivePhase.INTERPRET:
            self.workspace.world_hypotheses.extend(self._strings(output))
        elif phase == CognitivePhase.IMAGINE:
            self.workspace.possibilities.extend(self._strings(output))
        elif phase == CognitivePhase.CHOOSE:
            self.workspace.selected_option = str(output)
        elif phase == CognitivePhase.EVALUATE:
            self.workspace.focus.extend(self._strings(output))
        elif phase == CognitivePhase.EXPERIENCE:
            surprises = output.get("surprises", []) if isinstance(output, dict) else []
            self.workspace.surprises.extend(self._strings(surprises))
        elif phase == CognitivePhase.LEARN:
            questions = output.get("unresolved_questions", []) if isinstance(output, dict) else []
            self.workspace.unresolved_questions.extend(self._strings(questions))

    @staticmethod
    def _strings(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value]
        return [str(value)]

    def snapshot(self) -> dict[str, Any]:
        return {
            "workspace": asdict(self.workspace),
            "history": [
                {
                    "cycle_id": item.cycle_id,
                    "input_id": item.input_id,
                    "completed_phases": [phase.value for phase in item.completed_phases],
                    "stopped_at": item.stopped_at.value if item.stopped_at else None,
                    "error": item.error,
                }
                for item in self.history[-100:]
            ],
        }
