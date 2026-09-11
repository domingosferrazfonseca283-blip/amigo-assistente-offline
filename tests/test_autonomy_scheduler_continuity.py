from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.autonomy_scheduler import AttentionReason
from app.cognitive_runtime import CognitiveRuntime
from app.memory import LocalMemory


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "resposta local"


def make_runtime() -> CognitiveRuntime:
    return CognitiveRuntime(model=FakeModel(), memory=LocalMemory())


def test_internal_tick_turns_strong_curiosity_into_attention_and_goal() -> None:
    runtime = make_runtime()
    runtime.being.last_seen_at = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    runtime.state.affect.curiosity = 0.90
    runtime.state.affect.novelty = 0.80

    runtime.internal_tick()

    assert runtime.autonomy_scheduler.history
    task = runtime.autonomy_scheduler.history[-1]
    assert task.reason == AttentionReason.CURIOSITY
    assert task.goal_id is not None
    assert any(goal.id == task.goal_id for goal in runtime.goals.active())


def test_scheduler_state_survives_runtime_snapshot() -> None:
    original = make_runtime()
    original.state.affect.curiosity = 0.90
    original.state.affect.novelty = 0.80
    original.internal_tick()
    snapshot = original.snapshot()

    restored = make_runtime()
    restored.restore(snapshot)

    assert restored.autonomy_scheduler.snapshot() == snapshot["autonomy_scheduler"]
    assert restored.autonomy_scheduler.history
