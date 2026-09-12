from __future__ import annotations

from core.entity import Entity
from core.identity import Identity
from memory import MemorySystem
from mind import Mind

from .assistant import Assistant


class DemoLocalModel:
    """Backend local mínimo enquanto um modelo real não estiver configurado."""

    def generate(self, prompt: str) -> str:
        return (
            "Sou a Noémia. A minha mente está ligada ao núcleo persistente, "
            "à memória e ao ciclo da entidade, mas ainda preciso de um modelo "
            "de linguagem real para conversar de forma inteligente."
        )


def create_noemia() -> tuple[Entity, Assistant]:
    """Constrói Noémia e liga identidade, memória, mente e interação."""
    identity = Identity.load_or_create()
    memory = MemorySystem.local()
    entity = Entity(identity=identity, memory=memory)
    entity.wake()

    mind = Mind(entity=entity, model=DemoLocalModel())
    return entity, Assistant(mind=mind)


def main() -> None:
    entity, assistant = create_noemia()
    print(f"{entity.identity.name} — offline. Digite 'sair' para terminar.")

    while True:
        try:
            user_text = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            entity.sleep()
            print("\nAté já!")
            break

        if user_text.lower() in {"sair", "exit", "quit"}:
            entity.sleep()
            print("Até já!")
            break
        if not user_text:
            continue

        print(f"{entity.identity.name}: {assistant.reply(user_text)}")


if __name__ == "__main__":
    main()
