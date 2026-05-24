import threading
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, ProgressBar, RichLog
from textual.containers import Vertical, Horizontal
from models import InstallConfig, InstallType
import chroot_utils
import disk_utils
import profile_merger
import use_wizard
import subprocess

PROFILES_DIR = Path(__file__).parent.parent / "profiles"
MOUNT = "/mnt/gentra"

BASE_SERVICES = [
    "NetworkManager", "iwd", "systemd-resolved",
    "pipewire", "pipewire-pulse", "wireplumber",
]


class ProgressScreen(Screen):
    """Screen 7: Live install progress."""

    CSS = """
    ProgressScreen { align: center middle; }
    Vertical { width: 72; height: 90%; border: round $primary; padding: 1 2; }
    Label.title { text-style: bold; margin-bottom: 1; }
    ProgressBar { margin-bottom: 1; }
    RichLog { height: 1fr; border: round $surface; }
    Horizontal { align: center middle; margin-top: 1; }
    Button { display: none; }
    Button.show { display: block; }
    """

    def __init__(self, config: InstallConfig):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Installing Gentra...", classes="title")
            yield ProgressBar(total=100, id="bar", show_eta=False)
            yield RichLog(id="log", highlight=True, markup=True)
            with Horizontal():
                yield Button("Reboot now", variant="primary", id="reboot", classes="")

    def on_mount(self) -> None:
        threading.Thread(target=self._run_install, daemon=True).start()

    def _log(self, msg: str) -> None:
        self.call_from_thread(self.query_one("#log", RichLog).write, msg)

    def _set_progress(self, pct: float) -> None:
        self.call_from_thread(self.query_one("#bar", ProgressBar).update, progress=pct)

    def _run_install(self) -> None:
        try:
            self._do_install()
            self._log("[bold green]✓ Installation complete! You can now reboot.[/]")
            self.call_from_thread(
                self.query_one("#reboot", Button).add_class, "show"
            )
        except Exception as e:
            self._log(f"[bold red]✗ Installation failed: {e}[/]")

    def _do_install(self) -> None:
        config = self.config
        plan = disk_utils.auto_partition_plan(config.disk, config.swap_gb)

        steps = [
            ("Partitioning disk", self._partition, plan),
            ("Formatting partitions", self._format, plan, config.filesystem.value),
            ("Mounting filesystems", self._mount, plan),
            ("Unpacking stage3", self._unpack_stage3),
            ("Writing Portage config", self._write_portage, config),
            ("Installing kernel", self._install_kernel, config),
            ("Installing desktop environment", self._install_de, config),
            ("Installing base packages", self._install_base),
            ("Creating user account", self._create_user, config),
            ("Enabling services", self._enable_services),
            ("Installing bootloader", self._install_bootloader, config),
        ]

        for i, step in enumerate(steps):
            label, fn, *args = step
            self._log(f"[cyan]⟳[/] {label}...")
            fn(*args)
            self._log(f"[green]✓[/] {label}")
            self._set_progress((i + 1) / len(steps) * 100)

    def _partition(self, plan) -> None:
        cmd = ["parted", "-s", plan.disk, "mklabel", "gpt",
               "mkpart", "ESP", "fat32", "1MiB", "513MiB",
               "set", "1", "esp", "on"]
        if plan.swap:
            cmd += ["mkpart", "swap", "linux-swap", "513MiB",
                    f"{513 + plan.swap_gb * 1024}MiB"]
            cmd += ["mkpart", "root", "ext4",
                    f"{513 + plan.swap_gb * 1024}MiB", "100%"]
        else:
            cmd += ["mkpart", "root", "ext4", "513MiB", "100%"]
        subprocess.run(cmd, check=True)

    def _format(self, plan, fs: str) -> None:
        subprocess.run(["mkfs.fat", "-F32", plan.efi], check=True)
        if plan.swap:
            subprocess.run(["mkswap", plan.swap], check=True)
            subprocess.run(["swapon", plan.swap], check=True)
        fs_cmd = {"ext4": "mkfs.ext4", "btrfs": "mkfs.btrfs", "xfs": "mkfs.xfs"}
        subprocess.run([fs_cmd[fs], "-f", plan.root], check=True)

    def _mount(self, plan) -> None:
        subprocess.run(["mount", plan.root, MOUNT], check=True)
        Path(f"{MOUNT}/boot/efi").mkdir(parents=True, exist_ok=True)
        subprocess.run(["mount", plan.efi, f"{MOUNT}/boot/efi"], check=True)

    def _unpack_stage3(self) -> None:
        import urllib.request
        import tarfile
        url = "https://distfiles.gentoo.org/releases/amd64/autobuilds/current-stage3-amd64-systemd/stage3-amd64-systemd-latest.tar.xz"
        dest = "/tmp/stage3.tar.xz"
        urllib.request.urlretrieve(url, dest)
        with tarfile.open(dest, "r:xz") as tar:
            tar.extractall(MOUNT)

    def _write_portage(self, config: InstallConfig) -> None:
        profile_flags = profile_merger.load_profile(config.desktop.value, PROFILES_DIR)
        wizard_flags = use_wizard.answers_to_flags(config.use_answers)
        merged = profile_merger.merge_flags(profile_flags, wizard_flags)
        use_line = profile_merger.flags_to_make_conf(merged)
        chroot_utils.write_make_conf(use_line, profile=config.desktop.value)
        Path(f"{MOUNT}/etc/portage/repos.conf").mkdir(parents=True, exist_ok=True)
        chroot_utils.run_in_chroot(["emerge-webrsync"])

    def _install_kernel(self, config: InstallConfig) -> None:
        chroot_utils.install_kernel(config.kernel)

    def _install_de(self, config: InstallConfig) -> None:
        pkgs = chroot_utils.de_packages(config.desktop, config.install_type == InstallType.FULL)
        if pkgs:
            chroot_utils.emerge(pkgs)

    def _install_base(self) -> None:
        chroot_utils.emerge([
            "media-video/pipewire", "media-video/wireplumber",
            "net-misc/networkmanager", "net-wireless/iwd",
            "net-wireless/wireless-tools",
            "sys-boot/grub",
        ])

    def _create_user(self, config: InstallConfig) -> None:
        chroot_utils.create_user(config.username, config.full_name, config.password)
        hostname_file = Path(f"{MOUNT}/etc/hostname")
        hostname_file.write_text(config.hostname + "\n")

    def _enable_services(self) -> None:
        chroot_utils.enable_services(BASE_SERVICES)

    def _install_bootloader(self, config: InstallConfig) -> None:
        chroot_utils.install_bootloader(config.disk)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "reboot":
            subprocess.run(["reboot"])
