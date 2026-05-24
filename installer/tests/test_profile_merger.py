import pytest
from pathlib import Path
from profile_merger import load_profile, merge_flags, flags_to_make_conf

PROFILES_DIR = Path(__file__).parent.parent / "profiles"


def test_load_profile_kde():
    flags = load_profile("kde", PROFILES_DIR)
    assert "+qt6" in flags
    assert "+pipewire" in flags
    assert "-gnome" in flags


def test_load_profile_unknown_raises():
    with pytest.raises(FileNotFoundError):
        load_profile("nonexistent", PROFILES_DIR)


def test_merge_flags_wizard_adds_flags():
    profile_flags = ["+qt6", "+wayland", "-gnome"]
    wizard_flags = ["+bluetooth", "+cups"]
    result = merge_flags(profile_flags, wizard_flags)
    assert "+bluetooth" in result
    assert "+cups" in result
    assert "+qt6" in result


def test_merge_flags_profile_wins_conflict():
    # Profile says -gnome, wizard says +gnome (shouldn't happen but must be safe)
    profile_flags = ["-gnome", "+qt6"]
    wizard_flags = ["+gnome"]
    result = merge_flags(profile_flags, wizard_flags)
    # Profile takes precedence — -gnome wins
    assert "-gnome" in result
    assert "+gnome" not in result


def test_flags_to_make_conf():
    flags = ["+bluetooth", "-gnome", "+qt6"]
    result = flags_to_make_conf(flags)
    assert result == 'USE="bluetooth -gnome qt6"'


def test_flags_to_make_conf_strips_plus():
    flags = ["+foo", "-bar"]
    result = flags_to_make_conf(flags)
    assert "foo" in result
    assert "+foo" not in result
