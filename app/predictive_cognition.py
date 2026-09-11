from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .expectation_engine import Expectation, ExpectationEngine, ExpectationResult, ExpectationStatus
from .pattern_memory import PatternDetector, PatternKind, PatternMemory, PatternObservation
from .state_change import StateHistory


@dataclass
class Prediction:
    subject: str
    property: str
    predicted: Any
    confidence: float
    source_pattern_id: str
    pattern_kind: PatternKind
    evidence: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class PredictionObservation:
    prediction: Prediction
    expectation: Expectation


class PredictiveCognition:
    """Converte padrões locais suficientemente fortes em expectativas testáveis.

    Um padrão observado gera uma hipótese sobre o próximo estado, não uma
    afirmação de causalidade ou certeza.
    """

    def __init__(self, state_history: StateHistory, patterns: PatternMemory | None = None, detector: PatternDetector | None = None, expectations: ExpectationEngine | None = None, max_predictions: int = 2000) -> None:
        self.state_history = state_history
        self.patterns = patterns or PatternMemory()
        self.detector = detector or PatternDetector()
        self.expectations = expectations or ExpectationEngine()
        self.max_predictions = max_predictions
        self.predictions: list[Prediction] = []

    @staticmethod
    def _next_value(pattern: PatternObservation) -> Any | None:
        sequence = pattern.sequence
        if pattern.kind == PatternKind.STABLE and sequence:
            return sequence[-1]
        if pattern.kind == PatternKind.CYCLE and len(sequence) >= 4:
            return sequence[-4]
        if pattern.kind == PatternKind.REVERSAL and len(sequence) >= 3:
            return sequence[-2]
        return None

    def _active_learned_expectation(self, subject: str, property: str) -> Expectation | None:
        candidates = [item for item in self.expectations.active(limit=100) if item.subject == subject and item.property == property and item.source == "learned_pattern"]
        return max(candidates, key=lambda item: item.confidence, default=None)

    def learn_prediction(self, subject: str, property: str) -> PredictionObservation | None:
        found = self.detector.detect(self.state_history, self.patterns, subject=subject, property=property)
        candidates = [(pattern, self._next_value(pattern)) for pattern in found]
        candidates = [(pattern, predicted) for pattern, predicted in candidates if predicted is not None]
        if not candidates:
            return None

        pattern, predicted = max(candidates, key=lambda item: item[0].confidence)
        confidence = max(0.05, min(0.90, pattern.confidence * 0.85))
        evidence = list(dict.fromkeys([pattern.id, *pattern.evidence]))[-20:]

        current = self._active_learned_expectation(subject, property)
        if current is not None and self.expectations._same(current.expected, predicted):
            return PredictionObservation(Prediction(subject, property, predicted, current.confidence, pattern.id, pattern.kind, evidence), current)
        if current is not None:
            current.status = ExpectationStatus.EXPIRED

        prediction = Prediction(subject, property, predicted, confidence, pattern.id, pattern.kind, evidence)
        expectation = self.expectations.expect(subject, property, predicted, confidence=confidence, source="learned_pattern", evidence=evidence)
        self.predictions.append(prediction)
        self.predictions = self.predictions[-self.max_predictions:]
        return PredictionObservation(prediction, expectation)

    def observe_actual(self, subject: str, property: str, value: Any, *, confidence: float = 0.5, evidence: list[str] | None = None) -> ExpectationResult | None:
        return self.expectations.observe(subject, property, value, confidence=confidence, evidence=evidence)

    def observe_and_learn(self, subject: str, property: str, value: Any, *, source: str = "observation", confidence: float = 0.5, evidence: list[str] | None = None) -> tuple[ExpectationResult | None, PredictionObservation | None]:
        result = self.observe_actual(subject, property, value, confidence=confidence, evidence=evidence)
        self.state_history.observe(subject, property, value, source=source, confidence=confidence, evidence=evidence)
        learned = self.learn_prediction(subject, property)
        return result, learned

    def predict(self, subject: str, property: str) -> Expectation | None:
        return self.expectations.predict(subject, property)

    def snapshot(self) -> dict[str, Any]:
        return {"predictions": [asdict(item) | {"pattern_kind": item.pattern_kind.value} for item in self.predictions[-100:]]}
