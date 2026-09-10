from __future__ import annotations

from dataclasses import dataclass

from .cognitive_runtime import CognitiveRuntime, LocalKnowledge, LocalModel
from .memory import LocalMemory


class LocalVoice:
    def speak(self, text: str) -> None:
        """Converte texto em voz sem depender da internet."""
        raise NotImplementedError


@dataclass
class NoemiaCore:
    """Fachada pública da Noémia sobre o núcleo cognitivo persistente."""

    model: LocalModel
    memory: LocalMemory
    knowledge: LocalKnowledge | None = None
    voice: LocalVoice | None = None

    def __post_init__(self) -> None:
        self.runtime = CognitiveRuntime(
            model=self.model,
            memory=self.memory,
            knowledge=self.knowledge,
        )

    @property
    def session(self) -> list[dict]:
        return self.runtime.state.working_memory

    @property
    def turn_count(self) -> int:
        return self.runtime.state.turn_count

    def converse(self, user_text: str, speak: bool = False) -> str:
        text = user_text.strip()
        if not text:
            return ""

        # Percepção e atualização do estado acontecem antes da geração.
        self.runtime.perceive(text)
        response = self.runtime.think(text)

        if speak and self.voice is not None:
            self.voice.speak(response)
        return response

    def snapshot(self) -> dict:
        return self.runtime.snapshot()
