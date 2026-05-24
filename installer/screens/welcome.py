from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Select, Button
from textual.containers import Vertical, Horizontal
from models import InstallConfig

LANGUAGES = [("English (US)", "en_US.UTF-8"), ("English (UK)", "en_GB.UTF-8"),
             ("German", "de_DE.UTF-8"), ("French", "fr_FR.UTF-8"),
             ("Spanish", "es_ES.UTF-8"), ("Japanese", "ja_JP.UTF-8")]

KEYMAPS = [("US", "us"), ("UK", "gb"), ("German", "de"), ("French", "fr"),
           ("Spanish", "es"), ("Dvorak", "dvorak")]


class WelcomeScreen(Screen):
    """Screen 1: Language, keymap, timezone selection."""

    CSS = """
    WelcomeScreen { align: center middle; }
    Vertical { width: 60; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    Label.field { margin-top: 1; }
    Select { margin-bottom: 1; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Welcome to Gentra", classes="title")
            yield Label("Language:", classes="field")
            yield Select(LANGUAGES, value="en_US.UTF-8", id="language")
            yield Label("Keyboard layout:", classes="field")
            yield Select(KEYMAPS, value="us", id="keymap")
            yield Label("Timezone:", classes="field")
            yield Select([("Auto-detect", "auto"), ("UTC", "UTC"),
                          ("America/New_York", "America/New_York"),
                          ("America/Los_Angeles", "America/Los_Angeles"),
                          ("Europe/London", "Europe/London"),
                          ("Europe/Berlin", "Europe/Berlin"),
                          ("Asia/Tokyo", "Asia/Tokyo")],
                         value="auto", id="timezone")
            with Horizontal():
                yield Button("Next →", variant="primary", id="next")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next":
            self.config.language = self.query_one("#language", Select).value
            self.config.keymap = self.query_one("#keymap", Select).value
            tz = self.query_one("#timezone", Select).value
            self.config.timezone = tz if tz != "auto" else "UTC"
            self.app.push_screen("disk")
