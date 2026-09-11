from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .cognitive_events import CognitiveEvent, EventType


@dataclass
class BeingPulse:
    """Uma unidade de continuidade da entidade digital."""

    sequence: int
    timestamp: str
    reason: str
    phase: str
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BeingDrive:
    """Impulso interno que pode competir por atenção/objetivos."""

    name: str
    intensity: float
    reason: str
    suggested_focus: str


@dataclass
class NoemiaBeing:
    """Camada de continuidade de uma entidade digital persistente.

    Não declara consciência humana. Representa identidade, estado, necessidades
    e experiência acumuláveis ao longo do tempo.
    """

    identity_name: str = "Noémia"
    sequence: int = 0
    phase: str = "resting"
    last_seen_at: str | None = None
    needs: dict[str, float] = field(default_factory=lambda: {
        "connection": 0.5,
        "curiosity": 0.4,
        "novelty": 0.3,
        "reflection": 0.4,
        "rest": 0.2,
    })
    current_focus: str | None = None
    recent_pulses: list[BeingPulse] = field(default_factory=list)

    def pulse(self, reason: str, phase: str = "reflecting", notes: list[str] | None = None) -> BeingPulse:
        self.sequence += 1
        self.phase = phase
        self.last_seen_at = datetime.now(timezone.utc).isoformat()
        pulse = BeingPulse(self.sequence, self.last_seen_at, reason, phase, notes or [])
        self.recent_pulses.append(pulse)
        self.recent_pulses = self.recent_pulses[-64:]
        return pulse

    def set_focus(self, focus: str | None) -> None:
        self.current_focus = focus.strip() if focus else None

    def update_need(self, name: str, delta: float) -> None:
        value = self.needs.get(name, 0.0) + delta
        self.needs[name] = max(0.0, min(1.0, value))

    def _apply_elapsed_time(self) -> float:
        """Transforma tempo decorrido em pressão interna acumulável.

        O relógio não é tratado como emoção real: é apenas um mecanismo de
        continuidade que impede o estado interno de ficar congelado enquanto
        o processo está parado.
        """
        if not self.last_seen_at:
            return 0.0
        try:
            previous = datetime.fromisoformat(self.last_seen_at)
            if previous.tzinfo is None:
                previous = previous.replace(tzinfo=timezone.utc)
            elapsed_minutes = max(0.0, (datetime.now(timezone.utc) - previous).total_seconds() / 60.0)
        except ValueError:
            return 0.0

        # Crescimento limitado por tick: tempo longo aumenta pressão, mas não
        # permite que um telefone desligado durante semanas sature instantaneamente.
        pressure = min(elapsed_minutes, 60.0)
        self.update_need("connection", 0.0007 * pressure)
        self.update_need("curiosity", 0.0010 * pressure)
        self.update_need("novelty", 0.0008 * pressure)
        self.update_need("reflection", 0.0006 * pressure)
        return elapsed_minutes

    def drives(self, limit: int = 3) -> list[BeingDrive]:
        reasons = {
            "connection": ("aproximação", "verificar continuidade da relação"),
            "curiosity": ("curiosidade", "explorar algo ainda não compreendido"),
            "novelty": ("novidade", "procurar uma experiência ou informação nova"),
            "reflection": ("reflexão", "rever experiências e consolidar memória"),
            "rest": ("repouso", "reduzir atividade e consolidar estado"),
        }
        drives = [
            BeingDrive(name, max(0.0, min(1.0, value)), reasons.get(name, (name, "processar estado interno"))[0], reasons.get(name, (name, "processar estado interno"))[1])
            for name, value in self.needs.items()
        ]
        drives.sort(key=lambda drive: drive.intensity, reverse=True)
        return drives[:max(0, limit)]

    def strongest_drive(self) -> BeingDrive | None:
        drives = self.drives(1)
        return drives[0] if drives else None

    def internal_tick(self) -> BeingDrive | None:
        """Executa um ciclo interno, incluindo a pressão do tempo decorrido."""
        elapsed_minutes = self._apply_elapsed_time()
        self.update_need("curiosity", 0.01)
        self.update_need("novelty", 0.008)
        self.update_need("reflection", 0.006)
        self.update_need("connection", 0.004)
        drive = self.strongest_drive()
        if drive:
            self.set_focus(drive.suggested_focus)
            phase = "resting" if drive.name == "rest" else "reflecting"
            notes = [f"intensity={drive.intensity:.2f}"]
            if elapsed_minutes >= 1.0:
                notes.append(f"tempo_decorrido_min={elapsed_minutes:.1f}")
            self.pulse(f"impulso interno: {drive.name}", phase, notes)
        return drive

    def experience(self, event: CognitiveEvent) -> None:
        if event.type == EventType.USER_MESSAGE:
            self.update_need("connection", -0.08)
            self.update_need("novelty", -0.03)
            self.pulse("interação recebida", "perceiving", ["user_message"])
        elif event.type == EventType.MODEL_RESPONSE:
            self.update_need("connection", -0.04)
            self.pulse("resposta produzida", "expressing", ["model_response"])
        elif event.type == EventType.CONSOLIDATION:
            self.update_need("reflection", -0.12)
            self.pulse("memórias consolidadas", "resting", ["consolidation"])
        elif event.type == EventType.DECISION:
            self.pulse("decisão tomada", "deciding", ["decision"])

    def snapshot(self) -> dict[str, Any]:
        return {
            "identity_name": self.identity_name,
            "sequence": self.sequence,
            "phase": self.phase,
            "last_seen_at": self.last_seen_at,
            "needs": dict(self.needs),
            "current_focus": self.current_focus,
            "recent_pulses": [
                {"sequence": p.sequence, "timestamp": p.timestamp, "reason": p.reason, "phase": p.phase, "notes": list(p.notes)}
                for p in self.recent_pulses
            ],
        }

    @classmethod
    def restore(cls, data: dict[str, Any]) -> "NoemiaBeing":
        being = cls(
            identity_name=str(data.get("identity_name", "Noémia")),
            sequence=int(data.get("sequence", 0)),
            phase=str(data.get("phase", "resting")),
            last_seen_at=data.get("last_seen_at"),
            needs={str(k): float(v) for k, v in dict(data.get("needs", {})).items()},
            current_focus=data.get("current_focus"),
        )
        being.recent_pulses = [BeingPulse(
            int(item.get("sequence", 0)), str(item.get("timestamp", "")),
            str(item.get("reason", "")), str(item.get("phase", "resting")),
            list(item.get("notes", [])),
        ) for item in data.get("recent_pulses", [])][-64:]
        return being
