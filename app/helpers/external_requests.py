from typing import Dict

from app import __version__

EXTERNAL_REQUEST_TIMEOUT = 1


def get_request_headers() -> Dict[str, str]:
    """Get the headers used for requests to external APIs."""
    return {"User-Agent": f"ED-API/{__version__}"}


def get_request_timeout() -> int:
    """Get the timeout to use for requests to external APIs."""
    return 1
