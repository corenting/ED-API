from fastapi import APIRouter, Depends

from app.models.galnet import GalnetArticle
from app.models.language import Language
from app.services.galnet import GalnetService

router = APIRouter(prefix="/galnet", tags=["News & Galnet"])


@router.get("", response_model=list[GalnetArticle])
async def get_latest_articles(
    lang: Language = Language.ENGLISH,
    galnet_service: GalnetService = Depends(),
) -> list[GalnetArticle]:
    """Get latest Galnet news."""
    return await galnet_service.get_articles(lang)
