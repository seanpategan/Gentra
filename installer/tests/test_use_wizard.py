from use_wizard import QUESTIONS, answers_to_flags, visible_questions
from models import Desktop


def test_questions_have_required_fields():
    for q in QUESTIONS:
        assert q.id
        assert q.category
        assert q.label
        assert isinstance(q.flags_if_yes, list)
        assert isinstance(q.flags_if_no, list)
        assert isinstance(q.default, bool)


def test_answers_to_flags_yes():
    flags = answers_to_flags({"bluetooth": True})
    assert "+bluetooth" in flags
    assert "+bluez" in flags


def test_answers_to_flags_no():
    flags = answers_to_flags({"bluetooth": False})
    assert "-bluetooth" in flags
    assert "-bluez" in flags


def test_answers_to_flags_gaming_yes():
    flags = answers_to_flags({"gaming": True})
    assert "+steam" in flags
    assert "+vulkan" in flags


def test_visible_questions_hides_display_flags_for_kde():
    # KDE already locks wayland — display question should be hidden
    questions = visible_questions(Desktop.KDE)
    ids = [q.id for q in questions]
    assert "display_wayland" not in ids


def test_visible_questions_shows_display_for_xfce():
    # XFCE supports both X11 and Wayland — show the question
    questions = visible_questions(Desktop.XFCE)
    ids = [q.id for q in questions]
    assert "display_wayland" in ids
