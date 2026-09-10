from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .memory import LocalMemory
from .prompts import SYSTEM_PROMPT


class LocalModel(Protocol):
    def generate(self, prompt: str) -> str:
        """Gera texto usando um modelo instalado localmente."""


@dataclass
class Assistant:
    model: LocalModel
    memory: LocalMemory

    def reply(self, user_text: str) -> str:
        history = self.memory.recent()
        prompt_parts = [SYSTEM_PROMPT, "\nHistórico recente:"]
        for item in history:
            prompt_parts.append(f"{item['role']}: {item['content']}")
        prompt_parts.append(f"\nUsuário: {user_text}\nAmigo:")

        response = self.model.generate("\n".join(prompt_parts)).strip()
        self.memory.add("user", user_text)
        self.memory.add("assistant", response)
        return response
