from typing import Union

import httpx

from app import __version__


def get_httpx_client(async_client: bool = True) -> Union[httpx.AsyncClient, httpx.Client]:  # type: ignore
    """Get an httpx client with proper configuration."""
    client_class = httpx.AsyncClient if async_client else httpx.Client  # type: ignore
    return client_class(headers={"User-Agent": f"ED-API/{__version__}"}, timeout=1)  # type: ignore
