import httpx

from app.helpers.httpx import get_async_httpx_client
from app.models.exceptions import ContentFetchingError
from app.models.game_server_health import GameServerHealth


class GameServerHealthService:
    """Main class for the game server health service."""

    async def get_game_server_health(self) -> GameServerHealth:
        """Get the latest news articles.

        :raises ContentFetchingException: Unable to retrieve the health
        """
        url = "https://ed-server-status.orerve.net/"

        async with get_async_httpx_client() as client:
            try:
                api_response = await client.get(url)
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        return GameServerHealth(status=api_response.json()["status"])
