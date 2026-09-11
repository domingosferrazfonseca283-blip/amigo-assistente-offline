from app.drive_context import DriveContext
from app.noemia_being import NoemiaBeing


def test_drive_context_exposes_ranked_internal_impulses_without_actions():
    being = NoemiaBeing()
    being.update_need("curiosity", 0.5)
    being.update_need("connection", 0.2)

    context = DriveContext.from_being(being)

    assert context.dominant is not None
    assert context.dominant.name == "curiosidade"
    assert context.drives[0].intensity >= context.drives[-1].intensity
    assert context.focus is None
    assert "drives" in context.as_dict()
    assert "action" not in context.as_dict()


def test_drive_context_preserves_being_focus():
    being = NoemiaBeing()
    being.set_focus("consolidar memórias")

    context = DriveContext.from_being(being)

    assert context.focus == "consolidar memórias"
