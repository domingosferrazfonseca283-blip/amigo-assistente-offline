from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.noemia_being import NoemiaBeing


def test_elapsed_time_changes_internal_pressure() -> None:
    being = NoemiaBeing(last_seen_at=(datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat())
    before = dict(being.needs)

    being.internal_tick()

    assert being.sequence == 1
    assert being.last_seen_at is not None
    assert being.needs["curiosity"] > before["curiosity"]
    assert being.needs["connection"] > before["connection"]
    assert any("tempo_decorrido_min=" in note for note in being.recent_pulses[-1].notes)


def test_long_pause_is_bounded_per_tick() -> None:
    being = NoemiaBeing(last_seen_at=(datetime.now(timezone.utc) - timedelta(days=30)).isoformat())
    being.internal_tick()

    assert being.needs["curiosity"] <= 0.4 + 0.01 + 0.001 * 60
    assert being.needs["novelty"] <= 0.3 + 0.008 + 0.0008 * 60
