from __future__ import annotations

from dataclasses import dataclass

from .cognitive_events import CognitiveEvent, EventType
from .episodic_memory import EpisodicMemory
from .event_bus import EventBus
from .learning import LearningEngine
from .reflection import ReflectionEngine
from .semantic_memory import SemanticMemory


@dataclass
class ConsolidationReport:
    reflections: int
    adjusted_beliefs: int


class OfflineConsolidator:
    """Ciclo de consolidação executável sem rede, ideal para períodos de inatividade."""

    def __init__(self, episodes: EpisodicMemory, semantic: SemanticMemory, bus: EventBus | None = None) -> None:
        self.episodes = episodes
        self.semantic = semantic
        self.bus = bus
        self.reflection = ReflectionEngine()
        self.learning = LearningEngine()

    def run(self) -> ConsolidationReport:
        reflections = self.reflection.reflect(self.episodes, self.semantic)
        result = self.learning.learn_from_experience(self.episodes, self.semantic)
        if self.bus is not None:
            self.bus.publish(CognitiveEvent(
                EventType.CONSOLIDATION,
                {"reflections": len(reflections), "adjusted_beliefs": result.adjusted},
                source="offline_consolidation",
                importance=0.6,
            ))
        return ConsolidationReport(len(reflections), result.adjusted)
