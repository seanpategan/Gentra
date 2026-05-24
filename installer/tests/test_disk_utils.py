from unittest.mock import patch
from disk_utils import list_disks, Disk, auto_partition_plan, SwapPlan
import pytest

LSBLK_OUTPUT = b"""[
  {"name":"sda","size":"512110190592","type":"disk","model":"Samsung SSD 860"},
  {"name":"nvme0n1","size":"1000204886016","type":"disk","model":"WDC SN770"}
]"""


def test_list_disks_parses_lsblk():
    with patch("disk_utils.subprocess.run") as mock_run:
        mock_run.return_value.stdout = LSBLK_OUTPUT
        mock_run.return_value.returncode = 0
        disks = list_disks()
    assert len(disks) == 2
    assert disks[0].path == "/dev/sda"
    assert disks[0].size_gb == pytest.approx(476, abs=1)
    assert disks[0].model == "Samsung SSD 860"
    assert disks[1].path == "/dev/nvme0n1"


def test_auto_partition_plan_with_swap():
    plan = auto_partition_plan("/dev/sda", swap_gb=8)
    assert plan.efi == "/dev/sda1"
    assert plan.root == "/dev/sda2"
    assert plan.swap == "/dev/sda3"
    assert plan.swap_gb == 8


def test_auto_partition_plan_no_swap():
    plan = auto_partition_plan("/dev/sda", swap_gb=0)
    assert plan.swap is None


def test_auto_partition_plan_nvme_naming():
    plan = auto_partition_plan("/dev/nvme0n1", swap_gb=4)
    assert plan.efi == "/dev/nvme0n1p1"
    assert plan.root == "/dev/nvme0n1p2"
    assert plan.swap == "/dev/nvme0n1p3"
