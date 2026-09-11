from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class WorkspaceKind(StrEnum):
    PERCEPTION = "perception"
    MEMORY = "memory"
    GOAL = "goal"
    HYPOTHESIS = "hypothesis"
    EXPECTATION = "expectation"
    QUESTION = "question"
    POSSIBILITY = "possibility"
    SELF_SIGNAL = "self_signal"


@dataclass
class WorkspaceItem:
    content: str
    kind: WorkspaceKind
    salience: float = 0.5
    confidence: float = 0.5
    source: str = "internal"
    activated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class WorkspaceFocus:
    item_id: str
    content: str
    kind: WorkspaceKind
    score: float
    reasons: list[str] = field(default_factory=list)
    selected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GlobalWorkspace:
    """Espaço de trabalho cognitivo global: compete pelo foco entre sinais internos e externos."""

    def __init__(self, capacity: int = 32, focus_capacity: int = 5) -> None:
        self.capacity = capacity
        self.focus_capacity = focus_capacity
        self.items: list[WorkspaceItem] = []
        self.focus: list[WorkspaceFocus] = []
        self.cycle_count = 0

    def submit(
        self,
        content: str,
        kind: WorkspaceKind,
        *,
        salience: float = 0.5,
        confidence: float = 0.5,
        source: str = "internal",
    ) -> WorkspaceItem:
        item = WorkspaceItem(
            content=str(content),
            kind=kind,
            salience=max(0.0, min(1.0, salience)),
            confidence=max(0.0, min(1.0, confidence)),
            source=source,
        )
        self.items.append(item)
        self.items = self.items[-self.capacity :]
        return item

    def compete(self, *, curiosity: float = 0.0, uncertainty: float = 0.0, novelty: float = 0.0) -> list[WorkspaceFocus]:
        weights = {
            WorkspaceKind.PERCEPTION: 1.00,
            WorkspaceKind.GOAL: 0.95,
            WorkspaceKind.QUESTION: 0.90,
            WorkspaceKind.HYPOTHESIS: 0.82,
            WorkspaceKind.MEMORY: 0.78,
            WorkspaceKind.EXPECTATION: 0.76,
            WorkspaceKind.POSSIBILITY: 0.72,
            WorkspaceKind.SELF_SIGNAL: 0.68,
        }
        ranked: list[WorkspaceFocus] = []
        for item in self.items:
            score = item.salience * 0.55 + item.confidence * 0.20 + weights[item.kind] * 0.15
            reasons = [f"saliencia={item.salience:.2f}", f"confiança={item.confidence:.2f}"]
            if item.kind in {WorkspaceKind.QUESTION, WorkspaceKind.HYPOTHESIS}:
                score += uncertainty * 0.10
                reasons.append(f"incerteza={uncertainty:.2f}")
            if item.kind in {WorkspaceKind.POSSIBILITY, WorkspaceKind.MEMORY}:
                score += curiosity * 0.08
                reasons.append(f"curiosidade={curiosity:.2f}")
            if item.kind == WorkspaceKind.PERCEPTION:
                score += novelty * 0.08
                reasons.append(f"novidade={novelty:.2f}")
            ranked.append(WorkspaceFocus(item.id, item.content, item.kind, max(0.0, min(1.0, score)), reasons))
        ranked.sort(key=lambda item: item.score, reverse=True)
        self.focus = ranked[: self.focus_capacity]
        self.cycle_count += 1
        return list(self.focus)

    def active_context(self) -> list[str]:
        return [f"[{item.kind.value}] {item.content}" for item in self.focus]

    def clear_cycle(self) -> None:
        self.items = [item for item in self.items if item.kind in {WorkspaceKind.GOAL, WorkspaceKind.EXPECTATION, WorkspaceKind.SELF_SIGNAL}]
        self.focus.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "capacity": self.capacity,
            "focus_capacity": self.focus_capacity,
            "items": [asdict(item) | {"kind": item.kind.value} for item in self.items],
            "focus": [asdict(item) | {"kind": item.kind.value} for item in self.focus],
            "cycle_count": self.cycle_count,
        }
