from models import InstallConfig, Desktop, Filesystem, KernelChoice, InstallType

def test_install_config_defaults():
    config = InstallConfig()
    assert config.desktop is None
    assert config.filesystem == Filesystem.EXT4
    assert config.kernel == KernelChoice.DIST
    assert config.install_type == InstallType.FULL
    assert config.use_answers == {}

def test_install_config_fields():
    config = InstallConfig(
        language="en_US.UTF-8",
        keymap="us",
        timezone="America/New_York",
        disk="/dev/sda",
        filesystem=Filesystem.BTRFS,
        swap_gb=8,
        full_name="Sean Egan",
        username="seanegan",
        password="secret",
        hostname="gentra-box",
        desktop=Desktop.KDE,
        install_type=InstallType.BASE,
        use_answers={"bluetooth": True, "printing": False},
        kernel=KernelChoice.DIST,
    )
    assert config.username == "seanegan"
    assert config.desktop == Desktop.KDE
    assert config.use_answers["bluetooth"] is True
