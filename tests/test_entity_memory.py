from __future__ import annotations

from app.memory import LocalMemory
from core.entity import Entity
from core.identity import Identity
from memory import MemoryKind, MemorySystem, MemoryStore


def test_memory_survives_new_store_instance(tmp_path):
    path = tmp_path / "memory.sqlite3"
    first = MemorySystem(MemoryStore(path))
    record = first.remember_relationship("O utilizador prefere respostas diretas.", importance=0.9)

    second = MemorySystem(MemoryStore(path))
    found = second.recall("utilizador prefere respostas", limit=5)

    assert any(item.id == record.id for item in found)
    assert found[0].kind is MemoryKind.RELATIONAL


def test_memory_types_and_snapshot(tmp_path):
    memory = MemorySystem.local(str(tmp_path / "memory.sqlite3"))
    memory.remember_fact("O projeto funciona offline.")
    memory.remember_episode("A entidade iniciou o ciclo de vida.")

    assert memory.store.count() == 2
    snapshot = memory.snapshot()
    assert len(snapshot) == 2
    assert {item["kind"] for item in snapshot} == {"semantic", "episodic"}


def test_entity_uses_persistent_memory(tmp_path):
    memory = MemorySystem.local(str(tmp_path / "memory.sqlite3"))
    entity = Entity(
        identity=Identity(entity_id="noemia-test", name="Noémia"),
        memory=memory,
    )

    entity.remember("O utilizador quer continuidade.", kind=MemoryKind.RELATIONAL)

    restored = MemorySystem.local(str(tmp_path / "memory.sqlite3"))
    assert restored.store.count() == 1
    assert restored.recall("utilizador quer continuidade")[0].kind is MemoryKind.RELATIONAL


def test_legacy_app_memory_uses_entity_memory(tmp_path):
    memory = MemorySystem.local(str(tmp_path / "memory.sqlite3"))
    local = LocalMemory(memory)
    local.add("user", "Olá, Noémia.")
    local.add("assistant", "Olá.")

    recent = local.recent()
    assert [item["role"] for item in recent] == ["user", "assistant"]
    assert memory.store.count() == 2
