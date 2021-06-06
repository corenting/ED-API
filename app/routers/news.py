from typing import List

from fastapi import APIRouter, Depends

from app.models.language import Language
from app.models.news import NewsArticle
from app.routers.helpers.responses import dataclass_response
from app.services.news import NewsService

router = APIRouter()


@router.get("/news", tags=["News & Galnet"], response_model=List[NewsArticle])
@dataclass_response
async def get_latest_articles(
    lang: Language = Language.ENGLISH,
    news_service: NewsService = Depends(),
) -> List[NewsArticle]:
    """Get latest news."""
    return await news_service.get_articles(lang)
