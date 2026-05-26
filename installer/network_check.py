import socket


class NetworkError(Exception):
    pass


def check_internet() -> bool:
    """
    Check internet connectivity via TCP connection to 8.8.8.8:53 (DNS).
    Raises NetworkError if no connection. Returns True on success.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("8.8.8.8", 53))
        sock.close()
        return True
    except OSError:
        raise NetworkError(
            "No internet connection detected. "
            "Please connect to the internet and restart the installer."
        )
