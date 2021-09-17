from fastapi import APIRouter, Depends

from app.models.language import Language
from app.models.news import NewsArticle
from app.services.news import NewsService

router = APIRouter()


@router.get("/news", tags=["News & Galnet"], response_model=list[NewsArticle])
async def get_latest_articles(
    lang: Language = Language.ENGLISH,
    news_service: NewsService = Depends(),
) -> list[NewsArticle]:
    """Get latest news."""
    return await news_service.get_articles(lang)
