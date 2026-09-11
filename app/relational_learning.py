from __future__ import annotations

from dataclasses import dataclass
from collections import Counter

from .episodic_memory import EpisodicMemory
from .memory_association import AssociativeMemory


@dataclass
class Pattern:
    relation: str
    source: str
    target: str
    strength: float
    evidence: list[str]


@dataclass
class RelationalLearningResult:
    patterns_found: int
    links_reinforced: int


class RelationalLearningEngine:
    """Aprende relações repetidas sem transformar correlação em certeza factual."""

    def learn(self, episodes: EpisodicMemory, associations: AssociativeMemory) -> RelationalLearningResult:
        counts: Counter[tuple[str, str]] = Counter()
        evidence: dict[tuple[str, str], list[str]] = {}
        recent = episodes.episodes[-200:]
        for episode in recent:
            details = episode.details if isinstance(episode.details, dict) else {}
            subject = details.get("subject")
            value = details.get("value")
            if subject is None or value is None:
                continue
            key = (f"entity:{str(subject).lower()}", f"value:{str(value).lower()}")
            counts[key] += 1
            evidence.setdefault(key, []).append(episode.id)

        patterns = 0
        reinforced = 0
        for (source, target), count in counts.items():
            if count < 2:
                continue
            if source not in associations.nodes:
                continue
            associations.add_node(__import__("app.memory_association", fromlist=["MemoryNode"]).MemoryNode(target, "value", target.removeprefix("value:"), min(0.9, 0.4 + count * 0.05)))
            existing = next((link for link in associations.links if link.source == source and link.target == target and link.relation == "padrao-observado"), None)
            strength = min(0.9, 0.35 + count * 0.08)
            if existing is None:
                associations.connect(source, target, "padrao-observado", weight=strength, evidence=evidence[(source, target)][-10:])
            else:
                existing.weight = max(existing.weight, strength)
                existing.evidence = list(dict.fromkeys(existing.evidence + evidence[(source, target)]))[-10:]
                reinforced += 1
            patterns += 1

        return RelationalLearningResult(patterns, reinforced)
