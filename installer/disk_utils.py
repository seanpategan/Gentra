import json
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class Disk:
    path: str
    size_gb: float
    model: str


@dataclass
class PartitionPlan:
    disk: str
    efi: str
    root: str
    swap: Optional[str]
    swap_gb: int


# Alias so tests can import either name
SwapPlan = PartitionPlan


def list_disks() -> list[Disk]:
    """Return all block devices of type 'disk' via lsblk JSON output."""
    result = subprocess.run(
        ["lsblk", "-J", "-b", "-o", "NAME,SIZE,TYPE,MODEL", "-d"],
        capture_output=True,
    )
    data = json.loads(result.stdout)

    # Real lsblk wraps the list: {"blockdevices": [...]}
    # The test mock provides a bare list — handle both.
    if isinstance(data, dict):
        devices = data.get("blockdevices", [])
    else:
        devices = data

    disks = []
    for dev in devices:
        if dev.get("type") == "disk":
            disks.append(Disk(
                path=f"/dev/{dev['name']}",
                size_gb=int(dev["size"]) / (1024 ** 3),
                model=dev.get("model", "Unknown").strip(),
            ))
    return disks


def _part(disk: str, n: int) -> str:
    """Return partition path: /dev/sda1 or /dev/nvme0n1p1."""
    if "nvme" in disk or "mmcblk" in disk:
        return f"{disk}p{n}"
    return f"{disk}{n}"


def auto_partition_plan(disk: str, swap_gb: int) -> PartitionPlan:
    """
    Build a partition plan for the given disk.
    Layout: 512MB EFI | swap (optional) | root (remainder)
    """
    efi = _part(disk, 1)
    root = _part(disk, 2)
    if swap_gb > 0:
        swap = _part(disk, 3)
    else:
        swap = None

    return PartitionPlan(
        disk=disk,
        efi=efi,
        root=root,
        swap=swap,
        swap_gb=swap_gb,
    )
