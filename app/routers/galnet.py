from typing import List

from fastapi import APIRouter, Depends

from app.models.galnet import GalnetArticle
from app.models.language import Language
from app.routers.helpers.responses import dataclass_response
from app.services.galnet import GalnetService

router = APIRouter()


@router.get("/galnet", tags=["Galnet"], response_model=List[GalnetArticle])
@dataclass_response
async def get_latest_articles(
    lang: Language = Language.ENGLISH,
    galnet_service: GalnetService = Depends(),
) -> List[GalnetArticle]:
    """Get latest Galnet news."""
    return await galnet_service.get_articles(lang)
