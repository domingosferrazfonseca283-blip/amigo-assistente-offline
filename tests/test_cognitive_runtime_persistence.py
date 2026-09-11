from __future__ import annotations

from app.cognitive_runtime import CognitiveRuntime
from app.memory import LocalMemory


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "resposta local"


def make_runtime() -> CognitiveRuntime:
    return CognitiveRuntime(model=FakeModel(), memory=LocalMemory())


def test_runtime_restores_being_and_core_state() -> None:
    original = make_runtime()
    original.being.update_need("curiosity", 0.31)
    original.being.set_focus("consolidar uma memória")
    original.internal_tick()
    original.create_goal("consolidar uma memória", priority=0.8, source="autonomy")
    original.perceive("Quero continuidade")

    snapshot = original.snapshot()

    restored = make_runtime()
    restored.restore(snapshot)

    assert restored.being.snapshot() == snapshot["being"]
    assert restored.state.to_dict() == snapshot["state"]
    assert restored.world.to_dict() == snapshot["world"]
    assert restored.relationship.snapshot() == snapshot["relationship"]
    assert restored.goals.goals
    assert next(iter(restored.goals.goals.values())).title == "consolidar uma memória"

    sequence_before = restored.being.sequence
    restored.internal_tick()
    assert restored.being.sequence == sequence_before + 1
    assert restored.being.last_seen_at != snapshot["being"]["last_seen_at"]
