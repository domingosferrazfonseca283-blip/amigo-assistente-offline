from __future__ import annotations

from core.entity import Entity
from core.identity import Identity
from memory import MemorySystem
from mind import Mind


class FakeModel:
    def generate(self, prompt: str) -> str:
        assert "Entrada: Olá" in prompt
        return "Olá. Sou a Noémia."


def test_mind_recalls_memory_and_persists_response(tmp_path):
    memory = MemorySystem.local(str(tmp_path / "memory.sqlite3"))
    entity = Entity(
        identity=Identity(entity_id="noemia-test", name="Noémia"),
        memory=memory,
    )
    entity.remember("O utilizador gosta de respostas diretas.")

    result = Mind(entity, FakeModel()).think("Olá")

    assert result.response == "Olá. Sou a Noémia."
    assert result.decision == "responder ao utilizador"
    assert memory.store.count() == 3
    assert any(item.content == "Olá. Sou a Noémia." for item in memory.recent(5))
