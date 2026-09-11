from app.expectation_engine import ExpectationEngine, ExpectationStatus
from app.pattern_memory import PatternKind, PatternMemory
from app.predictive_cognition import PredictiveCognition
from app.state_change import StateHistory


def build(values):
    history = StateHistory()
    cognition = PredictiveCognition(history, PatternMemory(), expectations=ExpectationEngine())
    for value in values:
        cognition.observe_and_learn("user", "estado", value, confidence=0.9)
    return cognition


def test_stable_pattern_creates_prediction():
    cognition = build(["calmo", "calmo", "calmo"])
    expectation = cognition.predict("user", "estado")
    assert expectation is not None
    assert expectation.expected == "calmo"
    assert expectation.source == "learned_pattern"
    assert expectation.confidence < 0.78


def test_cycle_pattern_predicts_next_value():
    cognition = build(["A", "B", "A", "B"])
    expectation = cognition.predict("user", "estado")
    assert expectation is not None
    assert expectation.expected == "A"


def test_reversal_pattern_predicts_previous_alternative():
    cognition = build(["A", "B", "A"])
    expectation = cognition.predict("user", "estado")
    assert expectation is not None
    assert expectation.expected == "B"


def test_observation_measures_surprise_and_learns_again():
    cognition = build(["A", "B", "A", "B"])
    result, learned = cognition.observe_and_learn("user", "estado", "C", confidence=0.9)
    assert result is not None
    assert result.status == ExpectationStatus.VIOLATED
    assert result.surprise > 0
    assert learned is not None


def test_weak_trend_does_not_create_expectation():
    cognition = build(["A", "B"])
    assert cognition.predict("user", "estado") is None
