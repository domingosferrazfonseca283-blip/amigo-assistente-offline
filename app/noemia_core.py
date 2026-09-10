from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from .memory import LocalMemory
from .prompts import SYSTEM_PROMPT


class LocalModel(Protocol):
    def generate(self, prompt: str) -> str:
        """Gera uma resposta usando um modelo instalado localmente."""


class LocalKnowledge(Protocol):
    def search(self, query: str, limit: int = 5) -> list[str]:
        """Pesquisa apenas na base de conhecimento local."""


class LocalVoice(Protocol):
    def speak(self, text: str) -> None:
        """Converte texto em voz sem depender da internet."""


@dataclass
class NoemiaCore:
    """Núcleo conversacional da Noémia.

    A interface foi separada das capacidades para que a personalidade,
    memória e contexto continuem sendo o centro mesmo quando voz, Android
    ou ações do dispositivo forem adicionados.
    """

    model: LocalModel
    memory: LocalMemory
    knowledge: LocalKnowledge | None = None
    voice: LocalVoice | None = None
    session: list[dict[str, str]] = field(default_factory=list)
    turn_count: int = 0

    def converse(self, user_text: str, speak: bool = False) -> str:
        text = user_text.strip()
        if not text:
            return ""

        context = self._context(text)
        prompt = self._build_prompt(text, context)
        response = self.model.generate(prompt).strip()
        if not response:
            response = "Estou aqui. Pode continuar."

        now = datetime.now(timezone.utc).isoformat()
        self.memory.add("user", text)
        self.memory.add("assistant", response)
        self.session.extend([
            {"role": "user", "content": text, "time": now},
            {"role": "assistant", "content": response, "time": now},
        ])
        self.turn_count += 1

        if speak and self.voice is not None:
            self.voice.speak(response)
        return response

    def _context(self, query: str) -> list[str]:
        if self.knowledge is None:
            return []
        try:
            return self.knowledge.search(query, limit=5)
        except Exception:
            # Uma falha da base local não deve derrubar a conversa.
            return []

    def _build_prompt(self, user_text: str, knowledge: list[str]) -> str:
        parts = [SYSTEM_PROMPT, "\nEstado da sessão:"]
        parts.append(f"Turnos nesta sessão: {self.turn_count}")

        recent = self.memory.recent(limit=16)
        if recent:
            parts.append("\nMemória/conversa recente:")
            for item in recent:
                parts.append(f"{item['role']}: {item['content']}")

        if knowledge:
            parts.append("\nConhecimento local relevante (não invente além dele):")
            for item in knowledge:
                parts.append(f"- {item}")

        parts.append(f"\nUsuário: {user_text}\nNoémia:")
        return "\n".join(parts)
