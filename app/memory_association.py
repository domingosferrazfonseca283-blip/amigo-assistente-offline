from __future__ import annotations

from dataclasses import dataclass, field
from math import log
from typing import Iterable


@dataclass
class MemoryNode:
    id: str
    kind: str
    label: str
    weight: float = 0.5
    tags: set[str] = field(default_factory=set)


@dataclass
class MemoryLink:
    source: str
    target: str
    relation: str
    weight: float = 0.5
    evidence: list[str] = field(default_factory=list)


class AssociativeMemory:
    """Índice local de relações entre memórias, separado do armazenamento bruto."""

    def __init__(self) -> None:
        self.nodes: dict[str, MemoryNode] = {}
        self.links: list[MemoryLink] = []

    def add_node(self, node: MemoryNode) -> MemoryNode:
        self.nodes[node.id] = node
        return node

    def connect(self, source: str, target: str, relation: str, *, weight: float = 0.5, evidence: Iterable[str] = ()) -> MemoryLink:
        link = MemoryLink(source, target, relation, max(0.0, min(1.0, weight)), list(evidence))
        self.links.append(link)
        return link

    def activate(self, query: str, limit: int = 12) -> list[tuple[MemoryNode, float]]:
        terms = {t for t in query.lower().split() if t}
        scores: dict[str, float] = {}
        for node in self.nodes.values():
            text = f"{node.label} {' '.join(node.tags)}".lower()
            overlap = sum(1 for term in terms if term in text)
            if overlap:
                scores[node.id] = overlap + node.weight * 0.25

        frontier = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]
        activated = dict(frontier)
        changed = True
        while changed and len(activated) < limit:
            changed = False
            for link in self.links:
                if link.source in activated and link.target in self.nodes and link.target not in activated:
                    score = activated[link.source] * link.weight * 0.35
                    if score >= 0.15:
                        activated[link.target] = score
                        changed = True
                if link.target in activated and link.source in self.nodes and link.source not in activated:
                    score = activated[link.target] * link.weight * 0.35
                    if score >= 0.15:
                        activated[link.source] = score
                        changed = True
                if len(activated) >= limit:
                    break

        return sorted(((self.nodes[node_id], score) for node_id, score in activated.items()), key=lambda item: item[1], reverse=True)[:limit]

    def reinforce(self, source: str, target: str, amount: float = 0.05) -> None:
        for link in self.links:
            if link.source == source and link.target == target:
                link.weight = min(1.0, link.weight + amount)

    def decay(self, amount: float = 0.01) -> None:
        for link in self.links:
            link.weight = max(0.05, link.weight - amount)

    def snapshot(self) -> dict:
        return {
            "nodes": [
                {"id": n.id, "kind": n.kind, "label": n.label, "weight": n.weight, "tags": sorted(n.tags)}
                for n in self.nodes.values()
            ],
            "links": [
                {"source": l.source, "target": l.target, "relation": l.relation, "weight": l.weight, "evidence": l.evidence}
                for l in self.links
            ],
        }
