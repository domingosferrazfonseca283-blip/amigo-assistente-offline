from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .episodic_memory import Episode, EpisodicMemory
from .memory_association import AssociativeMemory
from .memory_context import ContextualMemory, MemoryContext
from .semantic_memory import Belief, SemanticMemory


@dataclass
class MemoryMatch:
    kind: str
    item: Episode | Belief
    score: float
    reasons: list[str]


class CognitiveMemoryRetriever:
    """Recuperação híbrida: lexical + associação + contexto + recência + saliência."""

    def __init__(self, episodes: EpisodicMemory, semantic: SemanticMemory, associations: AssociativeMemory) -> None:
        self.episodes = episodes
        self.semantic = semantic
        self.associations = associations
        self.contexts: dict[str, ContextualMemory] = {}

    def attach_context(self, memory_id: str, context: MemoryContext, valid_until: str | None = None) -> ContextualMemory:
        item = ContextualMemory(memory_id, context, context.started_at, valid_until)
        self.contexts[memory_id] = item
        return item

    def forget(self, memory_id: str) -> bool:
        item = self.contexts.get(memory_id)
        if item is None:
            return False
        item.deactivate()
        return True

    def retrieve(self, query: str, current_context: MemoryContext | None = None, limit: int = 10) -> list[MemoryMatch]:
        now = datetime.now(timezone.utc)
        matches: list[MemoryMatch] = []
        activated = {node.id: score for node, score in self.associations.activate(query, limit=max(limit * 2, 10))}
        terms = [term for term in query.lower().split() if term]

        for episode in self.episodes.episodes:
            text = f"{episode.summary} {episode.details}".lower()
            lexical = sum(1 for term in terms if term in text) / max(1, len(terms))
            association = activated.get(episode.id, 0.0) * 0.18
            age_days = max(0.0, (now - datetime.fromisoformat(episode.timestamp)).total_seconds() / 86400.0)
            recency = 0.20 / (1.0 + age_days / 7.0)
            context_score = self.contexts[episode.id].context.score(query, current_context) if episode.id in self.contexts and self.contexts[episode.id].is_valid(now) else 0.0
            score = lexical * 0.42 + association + episode.salience * 0.20 + recency + context_score
            if score > 0.08:
                reasons = []
                if lexical: reasons.append("conteúdo")
                if association: reasons.append("associação")
                if context_score: reasons.append("contexto")
                if recency > 0.1: reasons.append("recência")
                matches.append(MemoryMatch("episode", episode, score, reasons))

        for belief in self.semantic.beliefs.values():
            text = f"{belief.subject} {belief.predicate} {belief.value}".lower()
            lexical = sum(1 for term in terms if term in text) / max(1, len(terms))
            node_id = f"belief:{belief.id}"
            association = activated.get(node_id, 0.0) * 0.18
            score = lexical * 0.55 + association + belief.confidence * 0.22
            if score > 0.08:
                reasons = ["facto/crença"]
                if association: reasons.append("associação")
                matches.append(MemoryMatch("belief", belief, score, reasons))

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[: max(1, limit)]
