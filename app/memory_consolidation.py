from __future__ import annotations

from dataclasses import dataclass

from .episodic_memory import EpisodicMemory
from .memory_association import AssociativeMemory, MemoryNode
from .semantic_memory import SemanticMemory


@dataclass
class MemoryConsolidationResult:
    nodes_created: int
    links_created: int


class MemoryConsolidator:
    """Converte episódios e crenças em uma rede associativa local."""

    def consolidate(self, episodes: EpisodicMemory, semantic: SemanticMemory, associations: AssociativeMemory) -> MemoryConsolidationResult:
        nodes_before = len(associations.nodes)
        links_before = len(associations.links)

        for episode in episodes.episodes[-200:]:
            associations.add_node(MemoryNode(episode.id, "episode", episode.summary, episode.salience))
            details = episode.details if isinstance(episode.details, dict) else {}
            subject = details.get("subject")
            predicate = details.get("predicate")
            value = details.get("value")
            if subject:
                subject_id = f"entity:{str(subject).lower()}"
                associations.add_node(MemoryNode(subject_id, "entity", str(subject), 0.65))
                associations.connect(episode.id, subject_id, "refere-se-a", weight=0.7, evidence=[episode.id])
            if predicate and value is not None:
                fact_id = f"fact:{str(subject).lower()}:{str(predicate).lower()}:{str(value).lower()}"
                associations.add_node(MemoryNode(fact_id, "fact", f"{subject} {predicate} {value}", episode.salience))
                associations.connect(episode.id, fact_id, "suporta", weight=0.75, evidence=[episode.id])

        for belief in semantic.beliefs.values():
            fact_id = f"belief:{belief.id}"
            associations.add_node(MemoryNode(fact_id, "belief", f"{belief.subject} {belief.predicate} {belief.value}", belief.confidence))
            subject_id = f"entity:{belief.subject.lower()}"
            associations.add_node(MemoryNode(subject_id, "entity", belief.subject, 0.65))
            associations.connect(subject_id, fact_id, "possui-crença", weight=belief.confidence, evidence=[belief.id])

        return MemoryConsolidationResult(len(associations.nodes) - nodes_before, len(associations.links) - links_before)
