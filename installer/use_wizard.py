from dataclasses import dataclass
from models import Desktop


@dataclass
class UseQuestion:
    id: str
    category: str
    label: str
    flags_if_yes: list[str]
    flags_if_no: list[str]
    default: bool
    # Desktop profiles that already determine this flag — hide question for these DEs
    hidden_for: list[Desktop] = None

    def __post_init__(self):
        if self.hidden_for is None:
            self.hidden_for = []


QUESTIONS: list[UseQuestion] = [
    # Hardware
    UseQuestion(
        id="bluetooth",
        category="Hardware",
        label="Bluetooth support?",
        flags_if_yes=["+bluetooth", "+bluez"],
        flags_if_no=["-bluetooth", "-bluez"],
        default=True,
    ),
    UseQuestion(
        id="printing",
        category="Hardware",
        label="Printing support?",
        flags_if_yes=["+cups", "+cups-filters"],
        flags_if_no=["-cups", "-cups-filters"],
        default=True,
    ),
    UseQuestion(
        id="webcam",
        category="Hardware",
        label="Webcam support?",
        flags_if_yes=["+v4l", "+libv4l"],
        flags_if_no=["-v4l", "-libv4l"],
        default=True,
    ),
    # Media
    UseQuestion(
        id="codecs",
        category="Media",
        label="MP3, video, and codec support?",
        flags_if_yes=["+mp3", "+ffmpeg", "+gstreamer", "+libav"],
        flags_if_no=["-mp3", "-ffmpeg"],
        default=True,
    ),
    UseQuestion(
        id="dvd",
        category="Media",
        label="DVD playback support?",
        flags_if_yes=["+dvd", "+libdvdread", "+libdvdnav"],
        flags_if_no=["-dvd", "-libdvdread", "-libdvdnav"],
        default=False,
    ),
    # Features
    UseQuestion(
        id="gaming",
        category="Features",
        label="Gaming support (Steam, Wine, Vulkan, Proton)?",
        flags_if_yes=["+steam", "+wine", "+vulkan", "+proton"],
        flags_if_no=["-steam", "-wine"],
        default=False,
    ),
    UseQuestion(
        id="flatpak",
        category="Features",
        label="Flatpak support?",
        flags_if_yes=["+flatpak"],
        flags_if_no=["-flatpak"],
        default=False,
    ),
    # Privacy
    UseQuestion(
        id="telemetry",
        category="Privacy",
        label="Allow crash reporting and telemetry?",
        flags_if_yes=["+telemetry"],
        flags_if_no=["-telemetry"],
        default=False,
    ),
    # Display — hidden for DEs that already lock this
    UseQuestion(
        id="display_wayland",
        category="Display",
        label="Use Wayland display server (modern, recommended)?",
        flags_if_yes=["+wayland", "-X"],
        flags_if_no=["-wayland", "+X", "+xorg"],
        default=True,
        hidden_for=[Desktop.KDE, Desktop.GNOME, Desktop.HYPRLAND, Desktop.I3],
    ),
]


def answers_to_flags(answers: dict[str, bool]) -> list[str]:
    """Convert {question_id: bool} answers to a flat list of USE flag strings."""
    flags = []
    for question in QUESTIONS:
        if question.id in answers:
            if answers[question.id]:
                flags.extend(question.flags_if_yes)
            else:
                flags.extend(question.flags_if_no)
    return flags


def visible_questions(desktop: Desktop) -> list[UseQuestion]:
    """Return questions that should be shown for the given desktop (not pre-determined by DE profile)."""
    return [q for q in QUESTIONS if desktop not in q.hidden_for]
