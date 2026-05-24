from pathlib import Path


def load_profile(desktop: str, profiles_dir: Path) -> list[str]:
    """Load USE flags from a profile file. Returns list of flag strings like '+qt6', '-gnome'."""
    path = profiles_dir / f"use.{desktop}"
    if not path.exists():
        raise FileNotFoundError(f"No profile found for desktop: {desktop}")
    return [f for f in path.read_text().split() if f and f[0] in ("+", "-")]


def merge_flags(profile_flags: list[str], wizard_flags: list[str]) -> list[str]:
    """
    Merge DE profile flags with wizard answer flags.
    Profile flags take precedence: if profile sets -gnome, wizard cannot override to +gnome.
    """
    # Build a dict of flag_name -> full_flag from profile (profile wins)
    result: dict[str, str] = {}
    for flag in profile_flags:
        name = flag.lstrip("+-")
        result[name] = flag

    # Add wizard flags only if profile hasn't set them
    for flag in wizard_flags:
        name = flag.lstrip("+-")
        if name not in result:
            result[name] = flag

    return list(result.values())


def flags_to_make_conf(flags: list[str]) -> str:
    """Convert a list of flags to a USE= line for make.conf. Strips leading + signs."""
    formatted = []
    for flag in sorted(flags, key=lambda f: f.lstrip("+-")):
        if flag.startswith("+"):
            formatted.append(flag[1:])  # strip + sign, Portage doesn't use it
        else:
            formatted.append(flag)  # keep - sign
    return f'USE="{" ".join(formatted)}"'
