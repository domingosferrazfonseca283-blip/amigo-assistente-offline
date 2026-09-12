from __future__ import annotations

from core.identity import Identity
from memory import MemorySystem
from app.memory import LocalMemory


def test_identity_survives_recreation(tmp_path):
    path = tmp_path / "identity.json"
    first = Identity.load_or_create(path, name="Noémia")
    second = Identity.load_or_create(path, name="Outro nome")

    assert first.entity_id == second.entity_id
    assert second.name == "Noémia"


def test_app_memory_uses_entity_memory(tmp_path):
    memory = MemorySystem.local(str(tmp_path / "entity.sqlite3"))
    adapter = LocalMemory(memory)

    adapter.add("user", "A memória deve ser única.")
    recent = adapter.recent()

    assert len(recent) == 1
    assert recent[0]["role"] == "user"
    assert memory.store.count() == 1
