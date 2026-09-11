from app.autonomy import AutonomyEngine
from app.autonomy_scheduler import AutonomyScheduler
from app.goals import GoalManager
from app.internal_life import InternalActivity, InternalLife


def test_internal_life_selects_goal_without_external_action():
    goals = GoalManager()
    goals.add("Aprender preferências", 0.9, "autonomy")
    life = InternalLife(AutonomyScheduler(goals, AutonomyEngine()))
    results = life.tick(curiosity=0.2, uncertainty=0.1, novelty=0.1)
    assert len(results) == 1
    assert results[0].activity == InternalActivity.REVIEW_GOALS
    assert life.scheduler.pending == []


def test_internal_life_can_be_disabled():
    goals = GoalManager()
    life = InternalLife(AutonomyScheduler(goals, AutonomyEngine()))
    life.policy.enabled = False
    assert life.tick(curiosity=1.0, uncertainty=1.0, novelty=1.0) == []
