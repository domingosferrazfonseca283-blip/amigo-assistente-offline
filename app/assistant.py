from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mind import Mind


class LocalModel(Protocol):
    def generate(self, prompt: str) -> str:
        """Gera texto usando um modelo instalado localmente."""


@dataclass
class Assistant:
    """Adaptador de interação; a cognição pertence à Mind de Noémia."""

    mind: Mind

    def reply(self, user_text: str) -> str:
        result = self.mind.think(user_text)
        return result.response or (
            "Entendi a entrada, mas ainda não tenho um modelo de linguagem "
            "ligado à minha mente para formular uma resposta completa."
        )
