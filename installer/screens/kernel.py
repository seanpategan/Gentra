from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, RadioSet, RadioButton, Checkbox
from textual.containers import Vertical, Horizontal
from models import InstallConfig, KernelChoice


class KernelScreen(Screen):
    """Screen 6: Kernel choice — dist-kernel (default) or genkernel."""

    CSS = """
    KernelScreen { align: center middle; }
    Vertical { width: 64; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    Label.section { text-style: bold; margin-top: 1; margin-bottom: 0; }
    Label.note { color: $text-muted; margin-left: 2; margin-bottom: 1; }
    RadioSet { margin-bottom: 1; }
    Checkbox { margin-top: 1; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Kernel & Packages", classes="title")
            yield Label("Kernel", classes="section")
            with RadioSet(id="kernel"):
                yield RadioButton("Distribution kernel (recommended)", value=True, id="dist")
                yield RadioButton("Compile your own kernel", id="genkernel")
            yield Label("  dist-kernel: Pre-built, works on all hardware, zero config", classes="note")
            yield Label("  genkernel: ~30-40 min, optimized for your hardware", classes="note")
            yield Label("Package source", classes="section")
            yield Checkbox(
                "Use Gentoo official binary packages (faster installs)",
                value=True,
                id="binhost",
            )
            yield Label("  Downloads pre-compiled packages from Gentoo's servers instead of compiling", classes="note")
            with Horizontal():
                yield Button("← Back", id="back")
                yield Button("Next →", variant="primary", id="next")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            pressed = self.query_one("#kernel", RadioSet).pressed_button
            self.config.kernel = KernelChoice(pressed.id)
            self.config.use_binhost = self.query_one("#binhost", Checkbox).value
            self.app.push_screen("progress")
