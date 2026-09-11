from app.drive_context import DriveContext
from app.noemia_being import NoemiaBeing
from app.noemia_life_loop import NoemiaLifeLoop


class FakeGoals:
    def __init__(self):
        self.items = []

    def active(self):
        return self.items


class FakeRuntime:
    def __init__(self):
        self.being = NoemiaBeing()
        self.goals = FakeGoals()
        self.persisted = 0
        self.consolidated = 0
        self.initiatives = 0

    def internal_tick(self):
        return DriveContext.from_being(self.being)

    def maybe_create_internal_goal(self, title, priority):
        goal = object()
        self.goals.items.append(goal)
        return goal

    def run_consolidation(self):
        self.consolidated += 1

    def evaluate_initiative(self, context):
        self.initiatives += 1
        return object()

    def snapshot(self):
        self.persisted += 1
        return {"being": self.being.snapshot()}


def test_tick_persists_entity_state_without_external_action():
    runtime = FakeRuntime()
    loop = NoemiaLifeLoop(runtime, persist=lambda _: None)

    result = loop.tick()

    assert result.sequence == 1
    assert runtime.persisted == 1
    assert result.initiative_created is False


def test_run_has_real_temporal_cycles_and_can_stop_after_n_cycles():
    runtime = FakeRuntime()
    sleeps = []
    loop = NoemiaLifeLoop(runtime, interval_seconds=0.01, sleep_fn=sleeps.append)

    completed = loop.run(cycles=3)

    assert completed == 3
    assert runtime.being.sequence == 3
    assert len(sleeps) == 2
    assert loop.running is False


def test_rest_drive_waits_instead_of_creating_initiative():
    runtime = FakeRuntime()
    runtime.being.update_need("rest", 0.9)
    runtime.being.update_need("curiosity", -0.5)
    runtime.being.update_need("novelty", -0.5)
    runtime.being.update_need("reflection", -0.5)
    runtime.being.update_need("connection", -0.5)
    loop = NoemiaLifeLoop(runtime)

    result = loop.tick()

    assert result.decision == "rest"
    assert runtime.initiatives == 0
    assert runtime.consolidated == 0
