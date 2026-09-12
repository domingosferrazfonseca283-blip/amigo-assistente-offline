from __future__ import annotations

from core.entity import Entity
from core.identity import Identity
from intelligence import ModelRouter
from memory import MemorySystem
from mind import Mind

from .assistant import Assistant


def create_noemia() -> tuple[Entity, Assistant]:
    """Constrói Noémia com identidade, memória, mente e inteligência real."""
    identity = Identity.load_or_create()
    memory = MemorySystem.local()
    entity = Entity(identity=identity, memory=memory)
    entity.wake()

    mind = Mind(entity=entity, model=ModelRouter.from_environment())
    return entity, Assistant(mind=mind)


def main() -> None:
    entity, assistant = create_noemia()
    print(f"{entity.identity.name} — online para raciocínio local/online. Digite 'sair' para terminar.")

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

        try:
            response = assistant.reply(user_text)
        except RuntimeError as exc:
            response = f"Não consegui aceder a um modelo de linguagem neste momento: {exc}"
        print(f"{entity.identity.name}: {response}")


if __name__ == "__main__":
    main()
