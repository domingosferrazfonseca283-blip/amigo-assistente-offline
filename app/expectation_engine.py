from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class ExpectationStatus(StrEnum):
    ACTIVE = "active"
    MET = "met"
    VIOLATED = "violated"
    EXPIRED = "expired"


@dataclass
class Expectation:
    subject: str
    property: str
    expected: Any
    confidence: float = 0.5
    source: str = "prediction"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str | None = None
    status: ExpectationStatus = ExpectationStatus.ACTIVE
    evidence: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class ExpectationResult:
    expectation_id: str
    observed: Any
    expected: Any
    surprise: float
    matched: bool
    status: ExpectationStatus
    confidence: float
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExpectationEngine:
    """Mantém previsões locais explícitas e mede o desvio entre esperado e observado."""

    def __init__(self, max_expectations: int = 5000, max_results: int = 5000) -> None:
        self.max_expectations = max_expectations
        self.max_results = max_results
        self.expectations: list[Expectation] = []
        self.results: list[ExpectationResult] = []

    @staticmethod
    def _same(left: Any, right: Any) -> bool:
        if isinstance(left, str) and isinstance(right, str):
            return left.strip().casefold() == right.strip().casefold()
        return left == right

    def expect(
        self,
        subject: str,
        property: str,
        expected: Any,
        confidence: float = 0.5,
        source: str = "prediction",
        expires_at: str | None = None,
        evidence: list[str] | None = None,
    ) -> Expectation:
        item = Expectation(
            subject=subject,
            property=property,
            expected=expected,
            confidence=max(0.0, min(1.0, confidence)),
            source=source,
            expires_at=expires_at,
            evidence=list(evidence or []),
        )
        self.expectations.append(item)
        self.expectations = self.expectations[-self.max_expectations:]
        return item

    def predict(self, subject: str, property: str) -> Expectation | None:
        active = [
            item for item in self.expectations
            if item.status == ExpectationStatus.ACTIVE
            and item.subject == subject
            and item.property == property
        ]
        return max(active, key=lambda item: item.confidence, default=None)

    def observe(
        self,
        subject: str,
        property: str,
        observed: Any,
        evidence: list[str] | None = None,
        confidence: float = 0.5,
    ) -> ExpectationResult | None:
        expectation = self.predict(subject, property)
        if expectation is None:
            return None

        matched = self._same(expectation.expected, observed)
        surprise = 0.0 if matched else expectation.confidence
        if matched:
            expectation.status = ExpectationStatus.MET
            expectation.confidence = min(0.98, expectation.confidence + 0.05 * max(0.1, confidence))
            reason = "O observado correspondeu à expectativa local."
        else:
            expectation.status = ExpectationStatus.VIOLATED
            expectation.confidence = max(0.05, expectation.confidence * 0.75)
            reason = "O observado divergiu da expectativa local; a previsão deve ser revista."
        expectation.evidence.extend(evidence or [])
        expectation.evidence = list(dict.fromkeys(expectation.evidence))[-20:]
        result = ExpectationResult(
            expectation_id=expectation.id,
            observed=observed,
            expected=expectation.expected,
            surprise=surprise,
            matched=matched,
            status=expectation.status,
            confidence=expectation.confidence,
            reason=reason,
        )
        self.results.append(result)
        self.results = self.results[-self.max_results:]
        return result

    def expire(self, now: datetime | None = None) -> int:
        current = now or datetime.now(timezone.utc)
        count = 0
        for item in self.expectations:
            if item.status != ExpectationStatus.ACTIVE or not item.expires_at:
                continue
            try:
                expiry = datetime.fromisoformat(item.expires_at)
            except ValueError:
                continue
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if expiry <= current:
                item.status = ExpectationStatus.EXPIRED
                count += 1
        return count

    def active(self, limit: int = 20) -> list[Expectation]:
        return [item for item in reversed(self.expectations) if item.status == ExpectationStatus.ACTIVE][:limit]

    def recent_results(self, limit: int = 20) -> list[ExpectationResult]:
        return list(reversed(self.results[-limit:]))

    def snapshot(self) -> dict[str, Any]:
        return {
            "expectations": [{**asdict(item), "status": item.status.value} for item in self.expectations],
            "results": [{**asdict(item), "status": item.status.value} for item in self.results],
        }
