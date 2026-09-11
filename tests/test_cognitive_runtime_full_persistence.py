from __future__ import annotations

from app.agency import ActionRisk, PermissionMode
from app.cognitive_runtime import CognitiveRuntime
from app.goals import GoalStatus
from app.memory_association import MemoryNode
from app.memory import LocalMemory


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "resposta local"


def make_runtime() -> CognitiveRuntime:
    return CognitiveRuntime(model=FakeModel(), memory=LocalMemory())


def test_runtime_restores_full_cognitive_continuity() -> None:
    original = make_runtime()
    original.being.update_need("curiosity", 0.91)
    original.being.set_focus("explorar continuidade")
    goal = original.create_goal("explorar continuidade", priority=0.9, source="autonomy")
    episode = original.episodic.record("experiência persistente", {"topic": "continuidade"}, importance=0.9)
    original.associations.add_node(MemoryNode(episode.id, "episode", episode.summary, episode.salience))
    original.semantic.learn_user_fact("utilizador", "valoriza", "continuidade")
    original.timeline.record("marco persistente", source="test", event_id="timeline-1")
    original.state_history.observe("Noémia", "fase", "reflexão", source="test", confidence=0.9)
    original.expectations.expect("Noémia", "próximo_passo", "refletir", confidence=0.8)
    original.decision_learning.record_outcome("decision-1", "explorar", "refletir", 0.7, 0.8, True)
    original.autonomy.policy.allow_self_initiated_goals = False
    original.agency.capabilities["internal_reflection"].permission = PermissionMode.ALLOW
    original.agency.capabilities["internal_reflection"].risk = ActionRisk.NONE
    original.internal_tick()
    snapshot = original.snapshot()

    restored = make_runtime()
    restored.restore(snapshot)

    assert restored.being.snapshot() == snapshot["being"]
    assert len(restored.episodic.episodes) == len(original.episodic.episodes)
    assert len(restored.semantic.beliefs) == len(original.semantic.beliefs)
    assert restored.associations.snapshot() == original.associations.snapshot()
    assert restored.timeline.snapshot() == original.timeline.snapshot()
    assert restored.state_history.snapshot() == original.state_history.snapshot()
    assert restored.decision_learning.snapshot() == original.decision_learning.snapshot()
    assert restored.expectations.snapshot() == original.expectations.snapshot()
    assert restored.autonomy.snapshot() == original.autonomy.snapshot()
    assert restored.workspace.snapshot() == original.workspace.snapshot()
    assert restored.goals.goals[goal.id].status == GoalStatus.ACTIVE
    assert restored.agency.capabilities["internal_reflection"].permission == PermissionMode.ALLOW
