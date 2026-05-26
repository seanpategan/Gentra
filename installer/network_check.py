import subprocess


class NetworkError(Exception):
    pass


def check_internet() -> bool:
    """
    Check internet connectivity by pinging 1.1.1.1.
    Raises NetworkError if no connection. Returns True on success.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "3", "archlinux.org"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise NetworkError(
                "No internet connection detected. "
                "Please connect to the internet and restart the installer."
            )
        return True
    except subprocess.TimeoutExpired:
        raise NetworkError(
            "No internet connection detected (timeout). "
            "Please connect to the internet and restart the installer."
        )
    except FileNotFoundError:
        raise NetworkError(
            "Could not check internet connection (ping not found). "
            "Please ensure you are connected to the internet."
        )
