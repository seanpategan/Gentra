import psutil
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Select, Button, RadioButton, RadioSet
from textual.containers import Vertical, Horizontal
from models import InstallConfig, Filesystem
from disk_utils import list_disks, Disk


class DiskScreen(Screen):
    """Screen 2: Disk selection, filesystem, swap."""

    CSS = """
    DiskScreen { align: center middle; }
    Vertical { width: 60; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    Label.field { margin-top: 1; }
    RadioSet { margin-bottom: 1; }
    Horizontal { align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config
        self.disks: list[Disk] = []

    def on_mount(self) -> None:
        self.disks = list_disks()
        disk_select = self.query_one("#disk", Select)
        disk_select.set_options(
            [(f"{d.path}  {d.size_gb:.0f}GB  {d.model}", d.path) for d in self.disks]
        )
        if self.disks:
            disk_select.value = self.disks[0].path

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Disk Setup", classes="title")
            yield Label("Select disk:", classes="field")
            yield Select([], id="disk")
            yield Label("Filesystem:", classes="field")
            with RadioSet(id="fs"):
                yield RadioButton("ext4 (recommended)", value=True, id="ext4")
                yield RadioButton("btrfs", id="btrfs")
                yield RadioButton("xfs", id="xfs")
            yield Label("Swap:", classes="field")
            yield Select([
                ("Auto (based on RAM)", "auto"),
                ("4 GB", "4"),
                ("8 GB", "8"),
                ("16 GB", "16"),
                ("None", "0"),
            ], value="auto", id="swap")
            with Horizontal():
                yield Button("← Back", id="back")
                yield Button("Next →", variant="primary", id="next")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "next":
            self.config.disk = self.query_one("#disk", Select).value
            fs_map = {"ext4": Filesystem.EXT4, "btrfs": Filesystem.BTRFS, "xfs": Filesystem.XFS}
            pressed = self.query_one("#fs", RadioSet).pressed_button
            self.config.filesystem = fs_map.get(pressed.id, Filesystem.EXT4)
            swap_val = self.query_one("#swap", Select).value
            ram_gb = psutil.virtual_memory().total // (1024 ** 3)
            self.config.swap_gb = ram_gb if swap_val == "auto" else int(swap_val)
            self.app.push_screen("user")
