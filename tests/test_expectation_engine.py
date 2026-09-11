from app.expectation_engine import ExpectationEngine, ExpectationStatus


def test_matching_expectation_is_met_and_not_surprising():
    engine = ExpectationEngine()
    item = engine.expect("user", "mood", "calm", confidence=0.8)

    result = engine.observe("user", "mood", "CALM", evidence=["obs-1"], confidence=0.9)

    assert result is not None
    assert result.matched is True
    assert result.surprise == 0.0
    assert result.status == ExpectationStatus.MET
    assert item.confidence > 0.8


def test_violation_creates_surprise_and_reduces_confidence():
    engine = ExpectationEngine()
    item = engine.expect("user", "mood", "calm", confidence=0.8)

    result = engine.observe("user", "mood", "agitated", evidence=["obs-2"])

    assert result is not None
    assert result.matched is False
    assert result.surprise == 0.8
    assert result.status == ExpectationStatus.VIOLATED
    assert item.confidence < 0.8


def test_only_active_expectations_are_predicted():
    engine = ExpectationEngine()
    first = engine.expect("user", "plan", "A", confidence=0.9)
    engine.observe("user", "plan", "B")
    engine.expect("user", "plan", "C", confidence=0.6)

    assert first.status == ExpectationStatus.VIOLATED
    assert engine.predict("user", "plan").expected == "C"
