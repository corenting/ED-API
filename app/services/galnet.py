import httpx
from dateutil.parser import parse

from app.helpers.frontier import get_frontier_api_url_for_language
from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingError
from app.models.galnet import GalnetArticle
from app.models.language import Language


class GalnetService:
    """Main class for the Galnet service."""

    BASE_PICTURE_PATH = "http://hosting.zaonce.net/elite-dangerous/galnet"

    async def get_articles(self, language: Language) -> list[GalnetArticle]:
        """Get the latest Galnet articles.

        :raises ContentFetchingException: Unable to retrieve the articles
        """
        url = f"{get_frontier_api_url_for_language(language)}/galnet_article?&sort=-published_at&page[offset]=0&page[limit]=12"
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(url)
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        articles = api_response.json()

        # Build response
        response_list: list[GalnetArticle] = []

        # Get picture, if null default to neutral one

        for item in articles["data"]:
            picture_name = (
                item["attributes"]["field_galnet_image"]
                or "NewsImageDiplomacyPressConference"
            )
            new_item = GalnetArticle(
                content=item["attributes"]["body"]["value"],
                uri=f"https://www.elitedangerous.com/news/galnet/{item['attributes']['field_slug']}",
                title=item["attributes"]["title"],
                published_date=parse(item["attributes"]["published_at"]).date(),  # type: ignore
                picture=f"{self.BASE_PICTURE_PATH}/{picture_name}.png",
            )
            response_list.append(new_item)

        return response_list
