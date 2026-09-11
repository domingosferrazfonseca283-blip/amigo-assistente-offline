from __future__ import annotations

import json

from app.internal_life import InternalActivity
from app.local_runtime_adapter import LocalRuntimeAdapter
from app.local_runtime_protocol import RuntimeCommand, RuntimeRequest


class FakeBus:
    def publish(self, _event):
        pass


class FakeMemory:
    def recent(self, limit=6):
        return [{"role": "user", "content": "memória local"}][:limit]


class FakeGoals:
    def top(self):
        return None


class FakeExpectations:
    def active(self, limit=20):
        return []

    def expire(self):
        return []


class FakeChanges:
    def recent_changes(self, limit=20):
        return []


class FakeRuntime:
    def __init__(self):
        self.memory = FakeMemory()
        self.goals = FakeGoals()
        self.expectations = FakeExpectations()
        self.state_history = FakeChanges()
        self.bus = FakeBus()
        self.perceived = []
        self.thought = []

    def perceive(self, text):
        self.perceived.append(text)

    def think(self, text):
        self.thought.append(text)
        return f"resposta: {text}"

    def snapshot(self):
        return {"test": True, "perceived": self.perceived, "thought": self.thought}


def adapter():
    return LocalRuntimeAdapter(FakeRuntime())


def test_perceive_dispatches_to_runtime():
    runtime = FakeRuntime()
    response = LocalRuntimeAdapter(runtime).dispatch(
        RuntimeRequest(RuntimeCommand.PERCEIVE, {"text": "olá"}, "r1")
    )
    assert response.ok
    assert response.request_id == "r1"
    assert runtime.perceived == ["olá"]


def test_think_dispatches_to_runtime():
    runtime = FakeRuntime()
    response = LocalRuntimeAdapter(runtime).dispatch(
        RuntimeRequest(RuntimeCommand.THINK, {"text": "continua"}, "r2")
    )
    assert response.ok
    assert response.payload["text"] == "resposta: continua"
    assert runtime.thought == ["continua"]


def test_internal_cycle_is_executable():
    response = adapter().dispatch(
        RuntimeRequest(RuntimeCommand.INTERNAL_CYCLE, {"activity": InternalActivity.REFLECT.value}, "r3")
    )
    assert response.ok
    assert response.payload["activity"] == InternalActivity.REFLECT.value
    assert "OBSERVE" in response.payload["completed_phases"]
    assert "RECALL" in response.payload["completed_phases"]


def test_snapshot_round_trip_payload():
    response = adapter().dispatch(RuntimeRequest(RuntimeCommand.SNAPSHOT, {}, "r4"))
    assert response.ok
    assert response.payload["test"] is True
    assert json.dumps(response.to_dict(), ensure_ascii=False)


def test_invalid_payload_returns_error_without_raising():
    response = adapter().dispatch(RuntimeRequest(RuntimeCommand.THINK, {}, "r5"))
    assert not response.ok
    assert response.request_id == "r5"
    assert "payload.text" in response.error
