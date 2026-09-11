from app.cognitive_cycle import CognitivePhase
from app.internal_cognitive_cycle import InternalCognitiveCycle
from app.internal_life import InternalActivity


class Memory:
    def recent(self, limit=6):
        return [{"role": "user", "content": "teste"}]


class Bus:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


class Goals:
    def top(self):
        return None


class Expectations:
    def active(self, limit=20):
        return []


class StateHistory:
    def recent_changes(self, limit=20):
        return []


class Runtime:
    memory = Memory()
    goals = Goals()
    expectations = Expectations()
    state_history = StateHistory()
    bus = Bus()


def test_internal_cycle_executes_real_cognitive_phases():
    runtime = Runtime()
    report = InternalCognitiveCycle(runtime).run(InternalActivity.REFLECT)
    assert report.activity == "reflect"
    assert CognitivePhase.OBSERVE.value in report.completed_phases
    assert CognitivePhase.RECALL.value in report.completed_phases
    assert CognitivePhase.INTERPRET.value in report.completed_phases
    assert CognitivePhase.DELIBERATE.value in report.completed_phases
    assert runtime.bus.events
