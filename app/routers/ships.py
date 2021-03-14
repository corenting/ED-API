from typing import List

from fastapi import APIRouter
from fastapi.responses import Response

from app.models.galnet import GalnetArticle
from app.models.language import Language
from app.routers.helpers.responses import dataclass_response
from app.routers.responses.galnet import GalnetArticle as GalnetArticleResponse
from app.services.galnet import GalnetService

router = APIRouter()


@router.get(
    "/ships/{ship_model}", tags=["Ships"], response_model=List[GalnetArticleResponse]
)
@dataclass_response
async def get_ship_picture(ship_model: str) -> Response:
    """Redirect to a picture corresponding the ship model."""
    return await GalnetService().get_articles(lang)
