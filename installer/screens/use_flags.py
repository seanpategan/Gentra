from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Checkbox, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer
from models import InstallConfig
from use_wizard import visible_questions


class UseFlagsScreen(Screen):
    """Screen 5: USE flag wizard — plain English questions with transparent flag display."""

    CSS = """
    UseFlagsScreen { align: center middle; }
    Vertical { width: 70; height: 90%; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    Label.category { text-style: bold; color: $accent; margin-top: 1; }
    ScrollableContainer { height: 1fr; border: round $surface; padding: 0 1; }
    .flag-hint { color: $text-muted; margin-left: 4; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        questions = visible_questions(self.config.desktop)
        with Vertical():
            yield Label("Configure Features", classes="title")
            with ScrollableContainer():
                current_category = None
                for q in questions:
                    if q.category != current_category:
                        current_category = q.category
                        yield Label(f"── {q.category} ──", classes="category")
                    yes_flags = " ".join(q.flags_if_yes)
                    yield Checkbox(q.label, value=q.default, id=f"q_{q.id}")
                    yield Label(f"→ {yes_flags}", classes="flag-hint")
            with Horizontal():
                yield Button("← Back", id="back")
                yield Button("Next →", variant="primary", id="next")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            questions = visible_questions(self.config.desktop)
            for q in questions:
                cb = self.query_one(f"#q_{q.id}", Checkbox)
                self.config.use_answers[q.id] = cb.value
            self.app.push_screen("kernel")
