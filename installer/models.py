from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Desktop(str, Enum):
    KDE = "kde"
    GNOME = "gnome"
    XFCE = "xfce"
    HYPRLAND = "hyprland"
    I3 = "i3"
    MINIMAL = "minimal"


class Filesystem(str, Enum):
    EXT4 = "ext4"
    BTRFS = "btrfs"
    XFS = "xfs"


class KernelChoice(str, Enum):
    DIST = "dist"
    GENKERNEL = "genkernel"


class InstallType(str, Enum):
    BASE = "base"
    FULL = "full"


@dataclass
class InstallConfig:
    language: str = "en_US.UTF-8"
    keymap: str = "us"
    timezone: str = "UTC"
    disk: Optional[str] = None
    filesystem: Filesystem = Filesystem.EXT4
    swap_gb: int = 0
    full_name: str = ""
    username: str = ""
    password: str = field(default="", repr=False)
    hostname: str = "gentra"
    desktop: Optional[Desktop] = None
    install_type: InstallType = InstallType.FULL
    use_answers: dict[str, bool] = field(default_factory=dict)
    kernel: KernelChoice = KernelChoice.DIST
    use_binhost: bool = True
