import httpx

from app import __version__

CLIENT_PARAMETERS = {"headers": {"User-Agent": f"ED-API/{__version__}"}, "timeout": 3}


def get_httpx_client() -> httpx.Client:
    """Get an httpx client with proper configuration."""
    return httpx.Client(**CLIENT_PARAMETERS)  # type: ignore


def get_aynsc_httpx_client() -> httpx.AsyncClient:
    """Get an httpx async client with proper configuration."""
    return httpx.AsyncClient(**CLIENT_PARAMETERS)  # type: ignore
