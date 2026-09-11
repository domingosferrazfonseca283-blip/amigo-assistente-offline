from __future__ import annotations

from typing import Any


def restore_runtime_core(runtime: Any, snapshot: dict[str, Any]) -> None:
    """Reconstrói o estado persistente essencial de um CognitiveRuntime.

    Mantém a restauração concentrada no estado que define continuidade da
    entidade. Componentes derivados são recriados pelo runtime.
    """
    from .cognitive_state import NoemiaState
    from .noemia_being import NoemiaBeing
    from .world_model import WorldModel

    runtime.state = NoemiaState.from_dict(dict(snapshot.get("state", {})))
    runtime.being = NoemiaBeing.restore(dict(snapshot.get("being", {})))
    runtime.world = WorldModel.from_dict(list(snapshot.get("world", [])))
    runtime.relationship.restore(snapshot.get("relationship"))
    runtime.affect.state = runtime.state.affect

    goals = snapshot.get("goals", [])
    runtime.goals.goals.clear()
    from .goals import Goal, GoalStatus
    for raw in goals:
        data = dict(raw)
        status = data.get("status", GoalStatus.ACTIVE)
        data["status"] = GoalStatus(status)
        goal = Goal(**data)
        runtime.goals.goals[goal.id] = goal
    runtime.state.active_goals = [goal.id for goal in runtime.goals.active()]
