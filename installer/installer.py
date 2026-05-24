#!/usr/bin/env python3
from textual.app import App
from models import InstallConfig
from network_check import check_internet, NetworkError
from screens.welcome import WelcomeScreen
from screens.disk import DiskScreen
from screens.user import UserScreen
from screens.desktop import DesktopScreen, InstallTypeScreen
from screens.use_flags import UseFlagsScreen
from screens.kernel import KernelScreen
from screens.progress import ProgressScreen


class GentraInstaller(App):
    """Gentra Linux installer."""

    TITLE = "Gentra Installer"
    CSS = """
    Screen { background: $surface; }
    """

    def __init__(self):
        super().__init__()
        self.config = InstallConfig()

    def on_mount(self) -> None:
        try:
            check_internet()
        except NetworkError as e:
            self.exit(message=str(e))
            return
        self.install_screen(WelcomeScreen(self.config), name="welcome")
        self.install_screen(DiskScreen(self.config), name="disk")
        self.install_screen(UserScreen(self.config), name="user")
        self.install_screen(DesktopScreen(self.config), name="desktop")
        self.install_screen(InstallTypeScreen(self.config), name="install_type")
        self.install_screen(UseFlagsScreen(self.config), name="use_flags")
        self.install_screen(KernelScreen(self.config), name="kernel")
        self.install_screen(ProgressScreen(self.config), name="progress")
        self.push_screen("welcome")


if __name__ == "__main__":
    GentraInstaller().run()
