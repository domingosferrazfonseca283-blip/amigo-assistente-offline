from app.noemia_being import NoemiaBeing


def test_needs_become_ranked_internal_drives():
    being = NoemiaBeing()
    being.update_need("curiosity", 0.5)
    being.update_need("rest", 0.1)

    drives = being.drives()

    assert drives
    assert drives[0].name == "curiosity"
    assert 0.0 <= drives[0].intensity <= 1.0


def test_internal_tick_updates_focus_and_pulse():
    being = NoemiaBeing()
    being.update_need("reflection", 0.5)

    before = being.sequence
    drive = being.internal_tick()

    assert drive is not None
    assert being.sequence == before + 1
    assert being.current_focus == drive.suggested_focus


def test_restore_preserves_needs_and_focus():
    original = NoemiaBeing()
    original.update_need("connection", 0.2)
    original.set_focus("consolidar memórias")
    original.pulse("teste", "reflecting")

    restored = NoemiaBeing.restore(original.snapshot())

    assert restored.needs == original.needs
    assert restored.current_focus == "consolidar memórias"
    assert restored.sequence == original.sequence
