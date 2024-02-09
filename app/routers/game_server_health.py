from fastapi import APIRouter, Depends

from app.models.game_server_health import GameServerHealth
from app.models.language import Language
from app.models.news import NewsArticle
from app.services.game_server_health import GameServerHealthService

router = APIRouter(prefix="/game_server_health", tags=["Game server health"])


@router.get("", response_model=GameServerHealth)
async def get_server_health(
    game_server_health_service: GameServerHealthService = Depends(),
) -> GameServerHealth:
    """Get the health of the game server."""
    return await game_server_health_service.get_game_server_health()
