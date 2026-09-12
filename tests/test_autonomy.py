from __future__ import annotations

from autonomy import AutonomyEngine, AutonomyPolicy
from core.entity import Entity
from core.identity import Identity
from memory import MemorySystem
from mind import Mind
from nervous_system import Event, NervousSystem


class NoModel:
    def generate(self, prompt: str) -> str:
        return "ok"


def test_autonomy_observes_without_owning_hardware(tmp_path):
    entity = Entity(
        identity=Identity(entity_id="autonomy-test", name="Noémia"),
        memory=MemorySystem.local(str(tmp_path / "memory.sqlite3")),
    )
    nervous = NervousSystem()
    received: list[Event] = []
    nervous.subscribe("environment.changed", received.append)

    engine = AutonomyEngine(
        entity=entity,
        mind=Mind(entity, NoModel()),
        nervous_system=nervous,
        policy=AutonomyPolicy(enabled=True),
        observer=lambda: [Event("environment.changed", {"value": "test"})],
    )

    engine.start()
    result = engine.tick()

    assert result.observed is True
    assert result.event_count == 1
    assert received[0].data["value"] == "test"
