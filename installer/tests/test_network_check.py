import socket
from unittest.mock import patch, MagicMock
from network_check import check_internet, NetworkError


def test_check_internet_success():
    mock_sock = MagicMock()
    with patch("network_check.socket.socket", return_value=mock_sock):
        assert check_internet() is True
    mock_sock.connect.assert_called_once_with(("8.8.8.8", 53))
    mock_sock.close.assert_called_once()


def test_check_internet_failure_raises():
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = OSError("Connection refused")
    with patch("network_check.socket.socket", return_value=mock_sock):
        try:
            check_internet()
            assert False, "Should have raised NetworkError"
        except NetworkError as e:
            assert "internet" in str(e).lower()


def test_check_internet_timeout_raises():
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = socket.timeout("timed out")
    with patch("network_check.socket.socket", return_value=mock_sock):
        try:
            check_internet()
            assert False, "Should have raised NetworkError"
        except NetworkError as e:
            assert "internet" in str(e).lower()
