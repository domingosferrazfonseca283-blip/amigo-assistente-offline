from __future__ import annotations

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
