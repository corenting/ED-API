import httpx

from app import __version__


def get_httpx_client() -> httpx.AsyncClient:  # type: ignore
    """Get an httpx client with proper configuration."""
    return httpx.AsyncClient(headers={"User-Agent": f"ED-API/{__version__}"}, timeout=1)  # type: ignore
