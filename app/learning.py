from __future__ import annotations

from dataclasses import dataclass

from .episodic_memory import EpisodicMemory
from .semantic_memory import Belief, BeliefKind, SemanticMemory


@dataclass
class LearningResult:
    learned: int
    adjusted: int


class LearningEngine:
    """Aprendizagem incremental conservadora: experiências alteram confiança, não inventam factos."""

    def learn_from_experience(self, episodes: EpisodicMemory, semantic: SemanticMemory) -> LearningResult:
        learned = 0
        adjusted = 0
        for episode in episodes.episodes[-50:]:
            outcome = episode.details.get("success") if isinstance(episode.details, dict) else None
            if outcome is None:
                continue
            for belief in semantic.beliefs.values():
                if belief.source != "consolidation":
                    continue
                if outcome:
                    old = belief.confidence
                    belief.confidence = min(0.99, belief.confidence + 0.01)
                    adjusted += belief.confidence != old
                else:
                    old = belief.confidence
                    belief.confidence = max(0.05, belief.confidence - 0.02)
                    adjusted += belief.confidence != old
        return LearningResult(learned, adjusted)
