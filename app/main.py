from __future__ import annotations

from .assistant import Assistant
from .memory import LocalMemory


class DemoLocalModel:
    """Backend temporário para validar a aplicação sem internet.

    Substitua por um adaptador de um modelo local (por exemplo, GGUF/llama.cpp)
    quando o modelo escolhido estiver instalado.
    """

    def generate(self, prompt: str) -> str:
        return (
            "O núcleo do Amigo está funcionando localmente. "
            "Agora falta ligar um modelo de linguagem local para eu conversar de verdade."
        )


def main() -> None:
    assistant = Assistant(model=DemoLocalModel(), memory=LocalMemory())
    print("Amigo — offline. Digite 'sair' para terminar.")

    while True:
        try:
            user_text = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté já!")
            break

        if user_text.lower() in {"sair", "exit", "quit"}:
            print("Até já!")
            break
        if not user_text:
            continue

        print(f"Amigo: {assistant.reply(user_text)}")


if __name__ == "__main__":
    main()
