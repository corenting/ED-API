import niquests
from loguru import logger

from app.helpers.niquests import get_async_niquests_session
from app.models.game_server_health import GameServerHealth


class GameServerHealthService:
    """Main class for the game server health service."""

    async def get_game_server_health(self) -> GameServerHealth:
        """Get the latest news articles.

        :raises ContentFetchingException: Unable to retrieve the health
        """
        url = "https://ed-server-status.orerve.net/"

        async with get_async_niquests_session() as session:
            try:
                api_response = await session.get(url)
                api_response.raise_for_status()
            except niquests.exceptions.RequestException:
                logger.opt(exception=True).warning("Could not fetch game server health")
                return GameServerHealth(status="Unknown")

        return GameServerHealth(status=api_response.json()["status"])
