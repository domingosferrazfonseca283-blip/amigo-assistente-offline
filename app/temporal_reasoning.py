from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .episodic_memory import EpisodicMemory
from .relationship_model import RelationshipModel
from .temporal_memory import TemporalMemory, TemporalRelation


@dataclass
class TemporalReasoningResult:
    events_linked: int
    repetitions_found: int
    possible_changes: int


class TemporalReasoningEngine:
    """Extrai relações temporais conservadoras de experiências locais."""

    def analyze(self, episodes: EpisodicMemory, relationship: RelationshipModel, timeline: TemporalMemory) -> TemporalReasoningResult:
        recent = episodes.episodes[-200:]
        linked = 0
        repetitions = 0
        changes = 0
        for previous, current in zip(recent, recent[1:]):
            try:
                before = datetime.fromisoformat(previous.timestamp)
                after = datetime.fromisoformat(current.timestamp)
            except ValueError:
                continue
            if after >= before:
                timeline.relate(previous.id, current.id, TemporalRelation.BEFORE, 0.95, [previous.id, current.id])
                timeline.relate(current.id, previous.id, TemporalRelation.AFTER, 0.95, [previous.id, current.id])
                linked += 1

        topic_events: dict[str, list[str]] = {}
        for episode in recent:
            details = episode.details if isinstance(episode.details, dict) else {}
            text = f"{episode.summary} {details}".lower()
            for topic in relationship.relationship.shared_topics:
                if topic in text:
                    topic_events.setdefault(topic, []).append(episode.id)

        for topic, event_ids in topic_events.items():
            if len(event_ids) < 2:
                continue
            repetitions += 1
            for source, target in zip(event_ids, event_ids[1:]):
                timeline.relate(source, target, TemporalRelation.REPEATS, 0.65, [source, target])

        return TemporalReasoningResult(linked, repetitions, changes)
