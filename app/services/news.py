from typing import List

import httpx
import pendulum

from app.helpers.frontier import get_frontier_api_url_for_language
from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingException
from app.models.language import Language
from app.models.news import NewsArticle


class NewsService:
    """Main class for the news service."""

    async def get_articles(self, language: Language) -> List[NewsArticle]:
        """Get the latest news articles.

        :raises ContentFetchingException: Unable to retrieve the articles
        """
        url = (
            f"{get_frontier_api_url_for_language(language)}/news_article"
            "?include=field_image_entity.field_media_image,field_site"
            "&filter[site][condition][path]=field_site.field_slug"
            "&filter[site][condition][operator]=CONTAINS"
            "&filter[site][condition][value]=elite-dangerous&sort[sort-published][path]=published_at"
            "&sort[sort-published][direction]=DESC&page[offset]=0&page[limit]=12"
        )

        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(url)
                api_response.raise_for_status()
            except httpx.HTTPError:  # type: ignore
                raise ContentFetchingException()

        articles = api_response.json()

        # Build response
        response_list: List[NewsArticle] = []

        for item in articles["data"]:
            new_item = NewsArticle(
                content=item["attributes"]["body"]["value"],
                uri=f"https://www.elitedangerous.com/news/{item['attributes']['field_slug']}",
                title=item["attributes"]["title"],
                published_date=pendulum.parse(item["attributes"]["published_at"]),  # type: ignore
            )
            response_list.append(new_item)

        return response_list
