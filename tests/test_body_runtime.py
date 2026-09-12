from __future__ import annotations

from body import Actuator, Body, BodyRuntime, Sense
from nervous_system import NervousSystem


class FakeBody:
    def has_sense(self, sense: Sense) -> bool:
        return sense is Sense.TOUCH

    def sense(self, sense: Sense):
        return {"pressure": 0.4}

    def can_act(self, actuator: Actuator) -> bool:
        return actuator is Actuator.SPEECH

    def act(self, actuator: Actuator, payload=None):
        return {"spoken": payload}


def test_body_runtime_bridges_perception_and_action():
    nervous = NervousSystem()
    runtime = BodyRuntime(Body(FakeBody()), nervous)

    perception = runtime.perceive(Sense.TOUCH)
    assert perception.type == "sense.touch"
    assert perception.data["value"] == {"pressure": 0.4}

    result = runtime.act(Actuator.SPEECH, "Olá")
    assert result == {"spoken": "Olá"}

    assert nervous.dispatch() == 2
