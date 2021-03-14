import httpx

from app import __version__


def get_httpx_client() -> httpx.Client:  # type: ignore
    return httpx.Client(headers={"User-Agent": f"ED-API/{__version__}"}, timeout=1)  # type: ignore
