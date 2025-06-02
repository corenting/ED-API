from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.models.galnet import GalnetArticle
from app.models.language import Language
from app.services.galnet import GalnetService

router = APIRouter(prefix="/galnet", tags=["News & Galnet"])


@router.get("", response_model=list[GalnetArticle])
async def get_latest_articles(
    lang: Language = Language.ENGLISH,
    page: Annotated[int, Query(ge=1)] = 1,
    galnet_service: GalnetService = Depends(),
) -> list[GalnetArticle]:
    """Get latest Galnet news."""
    return await galnet_service.get_articles(lang, page)
