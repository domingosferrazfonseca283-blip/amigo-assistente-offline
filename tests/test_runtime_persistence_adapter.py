from app.cognitive_runtime import CognitiveRuntime
from app.memory import LocalMemory
from app.runtime_persistence import restore_runtime_core


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "ok"


def test_restore_runtime_core_preserves_continuity() -> None:
    runtime = CognitiveRuntime(FakeModel(), LocalMemory())
    runtime.being.update_need("curiosity", 0.2)
    runtime.being.set_focus("memória")
    runtime.internal_tick()
    runtime.create_goal("memória", priority=0.8, source="autonomy")
    snapshot = runtime.snapshot()

    restored = CognitiveRuntime(FakeModel(), LocalMemory())
    restore_runtime_core(restored, snapshot)

    assert restored.being.snapshot() == snapshot["being"]
    assert restored.state.to_dict() == snapshot["state"]
    assert [g.title for g in restored.goals.active()] == ["memória"]
