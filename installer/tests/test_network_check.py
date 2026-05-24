from unittest.mock import patch, MagicMock
import subprocess
from network_check import check_internet, NetworkError


def test_check_internet_success():
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("network_check.subprocess.run", return_value=mock_result):
        assert check_internet() is True


def test_check_internet_failure_raises():
    with patch("network_check.subprocess.run", side_effect=subprocess.TimeoutExpired("ping", 5)):
        try:
            check_internet()
            assert False, "Should have raised NetworkError"
        except NetworkError as e:
            assert "internet" in str(e).lower()


def test_check_internet_bad_returncode_raises():
    mock_result = MagicMock()
    mock_result.returncode = 1
    with patch("network_check.subprocess.run", return_value=mock_result):
        try:
            check_internet()
            assert False, "Should have raised NetworkError"
        except NetworkError as e:
            assert "internet" in str(e).lower()
