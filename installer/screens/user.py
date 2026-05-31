import re
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Input, Button
from textual.containers import Vertical, Horizontal
from models import InstallConfig


class UserScreen(Screen):
    """Screen 3: User account creation."""

    CSS = """
    UserScreen { align: center middle; }
    Vertical { width: 60; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    Label.field { margin-top: 1; }
    Label.error { color: $error; }
    Input { margin-bottom: 1; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Create Your Account", classes="title")
            yield Label("Full name:", classes="field")
            yield Input(placeholder="e.g. Sean Egan", id="full_name")
            yield Label("Username:", classes="field")
            yield Input(placeholder="e.g. seanegan", id="username")
            yield Label("Password:", classes="field")
            yield Input(placeholder="Password", password=True, id="password")
            yield Label("Confirm password:", classes="field")
            yield Input(placeholder="Confirm password", password=True, id="confirm")
            yield Label("Hostname:", classes="field")
            yield Input(placeholder="e.g. my-gentra", value="gentra", id="hostname")
            yield Label("", id="error", classes="error")
            with Horizontal():
                yield Button("← Back", id="back")
                yield Button("Next →", variant="primary", id="next")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            error = self.query_one("#error", Label)
            full_name = self.query_one("#full_name", Input).value.strip()
            username = self.query_one("#username", Input).value.strip()
            password = self.query_one("#password", Input).value
            confirm = self.query_one("#confirm", Input).value
            hostname = self.query_one("#hostname", Input).value.strip()

            if not full_name:
                error.update("Full name is required.")
                return
            if not re.match(r"^[a-z_][a-z0-9_-]{0,31}$", username):
                error.update("Username must be lowercase letters, numbers, _ or - only.")
                return
            if password != confirm:
                error.update("Passwords do not match.")
                return
            if not re.match(r"^[a-zA-Z0-9-]+$", hostname):
                error.update("Hostname can only contain letters, numbers, and hyphens.")
                return

            self.config.full_name = full_name
            self.config.username = username
            self.config.password = password
            self.config.hostname = hostname
            error.update("")
            self.app.push_screen("desktop")
