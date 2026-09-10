from __future__ import annotations

from .cognitive_state import AffectState


class AffectEngine:
    """Variáveis operacionais para modular prioridade e comportamento; não simulam sentimentos humanos."""

    def __init__(self, state: AffectState | None = None) -> None:
        self.state = state or AffectState()

    def on_input(self, text: str) -> None:
        length_signal = min(1.0, len(text) / 500.0)
        self.state.novelty = min(1.0, self.state.novelty * 0.7 + 0.3 * length_signal)
        self.state.cognitive_load = min(1.0, self.state.cognitive_load * 0.8 + 0.2 * length_signal)
        self.state.curiosity = min(1.0, self.state.curiosity + 0.04)
        self.state.uncertainty = min(1.0, self.state.uncertainty + 0.02)
        self.state.clamp()

    def on_success(self) -> None:
        self.state.confidence = min(1.0, self.state.confidence + 0.04)
        self.state.uncertainty = max(0.0, self.state.uncertainty - 0.04)
        self.state.clamp()

    def on_failure(self) -> None:
        self.state.confidence = max(0.0, self.state.confidence - 0.06)
        self.state.uncertainty = min(1.0, self.state.uncertainty + 0.08)
        self.state.cognitive_load = min(1.0, self.state.cognitive_load + 0.05)
        self.state.clamp()
