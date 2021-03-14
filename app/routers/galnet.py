from typing import List

from fastapi import APIRouter

from app.models.galnet import GalnetArticle
from app.models.language import Language
from app.routers.helpers.responses import dataclass_response
from app.routers.responses.galnet import GalnetArticle as GalnetArticleResponse
from app.services.galnet import GalnetService

router = APIRouter()


@router.get("/galnet", tags=["Galnet"], response_model=List[GalnetArticleResponse])
@dataclass_response
async def get_latest_articles(lang: Language = Language.ENGLISH) -> List[GalnetArticle]:
    """Get latest Galnet news."""
    return await GalnetService().get_articles(lang)
