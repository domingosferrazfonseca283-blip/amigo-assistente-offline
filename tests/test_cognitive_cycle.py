from app.cognitive_cycle import CognitiveCycle, CognitiveCycleInput, CognitivePhase


def test_cycle_preserves_cognitive_order_and_workspace():
    cycle = CognitiveCycle()
    seen = []

    def observe(item, workspace):
        seen.append(CognitivePhase.OBSERVE)
        workspace.focus.append(item.payload["text"])

    def recall(item, workspace):
        seen.append(CognitivePhase.RECALL)
        return ["memória relevante"]

    def choose(item, workspace):
        seen.append(CognitivePhase.CHOOSE)
        assert workspace.memories == ["memória relevante"]
        return "continuar a explorar"

    cycle.register(CognitivePhase.OBSERVE, observe)
    cycle.register(CognitivePhase.RECALL, recall)
    cycle.register(CognitivePhase.CHOOSE, choose)

    result = cycle.run(CognitiveCycleInput("user", {"text": "olá"}), phases=(
        CognitivePhase.OBSERVE,
        CognitivePhase.RECALL,
        CognitivePhase.CHOOSE,
    ))

    assert seen == [CognitivePhase.OBSERVE, CognitivePhase.RECALL, CognitivePhase.CHOOSE]
    assert result.error is None
    assert result.workspace.selected_option == "continuar a explorar"


def test_cycle_isolates_transient_workspace_between_inputs():
    cycle = CognitiveCycle()
    cycle.register(CognitivePhase.RECALL, lambda item, workspace: ["memória antiga"])
    cycle.run(CognitiveCycleInput("user", {"text": "primeiro"}), phases=(CognitivePhase.RECALL,))
    assert cycle.workspace.memories == ["memória antiga"]

    cycle.run(CognitiveCycleInput("user", {"text": "segundo"}), phases=(), reset_transient=True)
    assert cycle.workspace.memories == []
