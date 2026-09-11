from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from time import sleep
from typing import Callable

from .cognitive_runtime import CognitiveRuntime
from .drive_context import DriveContext


@dataclass(frozen=True)
class LifeCycleResult:
    """Resultado de um ciclo autónomo; não representa uma ação externa executada."""

    sequence: int
    drive: str | None
    intensity: float
    decision: str
    goal_created: bool = False
    initiative_created: bool = False


class NoemiaLifeLoop:
    """Mantém a continuidade temporal da entidade fora da interação humana.

    O loop é deliberadamente separado da UI: cada ciclo observa o estado,
    atualiza impulsos, escolhe um foco cognitivo e pode consolidar memória ou
    preparar uma iniciativa. Nunca executa diretamente uma capacidade externa.
    """

    def __init__(
        self,
        runtime: CognitiveRuntime,
        persist: Callable[[dict], None] | None = None,
        interval_seconds: float = 30.0,
        goal_threshold: float = 0.72,
        initiative_threshold: float = 0.78,
        sleep_fn: Callable[[float], None] = sleep,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds deve ser positivo")
        self.runtime = runtime
        self.persist = persist
        self.interval_seconds = interval_seconds
        self.goal_threshold = goal_threshold
        self.initiative_threshold = initiative_threshold
        self.sleep_fn = sleep_fn
        self.running = False
        self.last_cycle_at: str | None = None

    def tick(self) -> LifeCycleResult:
        """Executa exatamente um ciclo, útil tanto para Android como para testes."""
        context = self.runtime.internal_tick()
        result = self._decide(context)
        self.last_cycle_at = datetime.now(timezone.utc).isoformat()
        if self.persist is not None:
            self.persist(self.runtime.snapshot())
        return result

    def _decide(self, context: DriveContext) -> LifeCycleResult:
        dominant = context.dominant
        if dominant is None:
            return LifeCycleResult(self.runtime.being.sequence, None, 0.0, "wait")

        if dominant.name == "rest":
            self.runtime.being.phase = "resting"
            return LifeCycleResult(self.runtime.being.sequence, dominant.name, dominant.intensity, "rest")

        goal_created = False
        active_goals = self.runtime.goals.active()
        if not active_goals and dominant.intensity >= self.goal_threshold:
            goal = self.runtime.maybe_create_internal_goal(dominant.suggested_focus, priority=min(0.95, dominant.intensity))
            goal_created = goal is not None

        if dominant.name == "reflection":
            self.runtime.run_consolidation()
            return LifeCycleResult(self.runtime.being.sequence, dominant.name, dominant.intensity, "consolidate", goal_created=goal_created)

        initiative_created = False
        if dominant.intensity >= self.initiative_threshold and self.runtime.goals.active():
            initiative_created = self.runtime.evaluate_initiative(context=f"impulso interno: {dominant.name}") is not None

        decision = "prepare_initiative" if initiative_created else ("pursue_goal" if self.runtime.goals.active() else "reflect")
        return LifeCycleResult(self.runtime.being.sequence, dominant.name, dominant.intensity, decision, goal_created=goal_created, initiative_created=initiative_created)

    def run(self, cycles: int | None = None) -> int:
        """Mantém a entidade viva até parar ou atingir o número de ciclos."""
        if cycles is not None and cycles < 0:
            raise ValueError("cycles não pode ser negativo")
        self.running = True
        completed = 0
        try:
            while self.running and (cycles is None or completed < cycles):
                self.tick()
                completed += 1
                if self.running and (cycles is None or completed < cycles):
                    self.sleep_fn(self.interval_seconds)
        finally:
            self.running = False
        return completed

    def stop(self) -> None:
        self.running = False
