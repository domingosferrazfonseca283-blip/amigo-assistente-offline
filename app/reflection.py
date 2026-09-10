from __future__ import annotations

from dataclasses import dataclass

from .episodic_memory import EpisodicMemory
from .semantic_memory import BeliefKind, SemanticMemory


@dataclass
class Reflection:
    insight: str
    evidence_ids: list[str]
    confidence: float


class ReflectionEngine:
    """Transforma experiências acumuladas em hipóteses e factos sem chamar a internet."""

    def reflect(self, episodes: EpisodicMemory, semantic: SemanticMemory) -> list[Reflection]:
        reflections: list[Reflection] = []
        for episode in episodes.episodes[-100:]:
            details = episode.details
            if not isinstance(details, dict):
                continue
            subject = details.get("subject")
            predicate = details.get("predicate")
            value = details.get("value")
            if subject and predicate and value is not None:
                existing = semantic.search(f"{subject} {predicate}", limit=20)
                if any(str(b.value) == str(value) for b in existing):
                    continue
                kind = BeliefKind.INFERRED if details.get("inferred") else BeliefKind.OBSERVED
                from .semantic_memory import Belief
                belief = Belief(str(subject), str(predicate), value, kind, min(0.95, max(0.35, episode.salience)), "consolidation")
                contradictions = semantic.contradictions(belief)
                if contradictions:
                    belief.confidence = min(belief.confidence, 0.45)
                semantic.upsert(belief)
                reflections.append(Reflection(
                    insight=f"{subject} → {predicate} → {value}",
                    evidence_ids=[episode.id],
                    confidence=belief.confidence,
                ))
        return reflections
