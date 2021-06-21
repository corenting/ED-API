import logging
from typing import Any, List, Optional

import httpx
import pendulum

from app.helpers.frontier import get_frontier_api_url_for_language
from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingException
from app.models.language import Language
from app.models.news import NewsArticle

logger = logging.getLogger(__name__)


def _get_picture_url_for_article(api_response: Any, article_id: str) -> Optional[str]:
    article = next((x for x in api_response["data"] if x["id"] == article_id), None)
    if article is None:
        return None

    article_include_id = article["relationships"]["field_image_entity"]["data"]["id"]

    # Get related include item to get picture ID
    related_include = next(
        (x for x in api_response["included"] if x["id"] == article_include_id), None
    )
    if related_include is None:
        return None
    article_picture_id = related_include["relationships"]["field_media_image"]["data"][
        "id"
    ]

    # Get picture
    picture = next(
        (x for x in api_response["included"] if x["id"] == article_picture_id), None
    )
    if picture is None:
        return None

    return picture["attributes"]["uri"]["url"]


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
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        articles = api_response.json()

        # Build response
        response_list: List[NewsArticle] = []

        for item in articles["data"]:

            try:
                picture = _get_picture_url_for_article(articles, item["id"])
            except Exception:
                logger.error(f"Couldn't get picture for article {item['id']}")
                picture = None

            new_item = NewsArticle(
                content=item["attributes"]["body"]["value"],
                uri=f"https://www.elitedangerous.com/news/{item['attributes']['field_slug']}",
                picture=picture,
                title=item["attributes"]["title"],
                published_date=pendulum.parse(item["attributes"]["published_at"]),  # type: ignore
            )
            response_list.append(new_item)

        return response_list
