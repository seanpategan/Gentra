from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, ListView, ListItem, RadioSet, RadioButton
from textual.containers import Vertical, Horizontal
from models import InstallConfig, Desktop, InstallType

DESKTOP_OPTIONS = [
    (Desktop.KDE, "KDE Plasma", "Modern, feature-rich (Qt6 + Wayland)"),
    (Desktop.GNOME, "GNOME", "Clean, opinionated (GTK + Wayland)"),
    (Desktop.XFCE, "XFCE", "Lightweight (GTK + X11/Wayland)"),
    (Desktop.HYPRLAND, "Hyprland", "Wayland tiling compositor"),
    (Desktop.I3, "i3", "X11 tiling window manager"),
    (Desktop.MINIMAL, "No DE / TTY", "Minimal, server or DIY"),
]

FULL_APPS = {
    Desktop.KDE: "Dolphin, Konsole, Kate, Okular, Gwenview, KCalc, Spectacle, Elisa",
    Desktop.GNOME: "Nautilus, GNOME Terminal, gedit, Evince, GNOME Calculator, Evolution",
    Desktop.XFCE: "Thunar, xfce4-terminal, Mousepad, Ristretto, Screenshooter",
    Desktop.HYPRLAND: "Thunar, foot, micro, zathura, imv",
    Desktop.I3: "Thunar, alacritty, micro, zathura, feh",
}


class DesktopScreen(Screen):
    """Screen 4: Desktop environment selection."""

    CSS = """
    DesktopScreen { align: center middle; }
    Vertical { width: 64; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    ListView { height: 8; border: round $surface; margin-bottom: 1; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Choose Your Desktop", classes="title")
            with ListView(id="de_list"):
                for i, (de, name, desc) in enumerate(DESKTOP_OPTIONS):
                    marker = "(X)" if i == 0 else "( )"
                    yield ListItem(Label(f"{marker} {name}  —  {desc}"), id=de.value)
            with Horizontal():
                yield Button("← Back", id="back")
                yield Button("Next →", variant="primary", id="next")

    def on_mount(self) -> None:
        self.query_one("#de_list", ListView).index = 0

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        lv = self.query_one("#de_list", ListView)
        for i, item in enumerate(lv.children):
            label = item.query_one(Label)
            text = label.renderable
            # strip existing marker
            if str(text).startswith("(X) ") or str(text).startswith("( ) "):
                text = str(text)[4:]
            marker = "(X)" if item is event.item else "( )"
            label.update(f"{marker} {text}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            lv = self.query_one("#de_list", ListView)
            if lv.index is None:
                return
            self.config.desktop = Desktop(list(lv.children)[lv.index].id)
            if self.config.desktop == Desktop.MINIMAL:
                self.config.install_type = InstallType.BASE
                self.app.push_screen("use_flags")
            else:
                self.app.push_screen("install_type")


class InstallTypeScreen(Screen):
    """Screen 4b: Base or full DE install."""

    CSS = """
    InstallTypeScreen { align: center middle; }
    Vertical { width: 64; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    Label.apps { color: $text-muted; margin-left: 2; }
    RadioSet { margin-bottom: 1; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        de_name = self.config.desktop.value.upper() if self.config.desktop else "DE"
        apps = FULL_APPS.get(self.config.desktop, "")
        with Vertical():
            yield Label(f"{de_name} — How much to install?", classes="title")
            with RadioSet(id="install_type"):
                yield RadioButton("Base desktop only", id="base")
                yield RadioButton("Full desktop + apps", value=True, id="full")
            yield Label(f"Full includes: {apps}", classes="apps")
            with Horizontal():
                yield Button("← Back", id="back")
                yield Button("Next →", variant="primary", id="next")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            pressed = self.query_one("#install_type", RadioSet).pressed_button
            self.config.install_type = InstallType(pressed.id)
            self.app.push_screen("use_flags")
