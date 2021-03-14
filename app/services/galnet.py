from typing import Any, Dict, List, Optional

import httpx
import pendulum

from app.helpers.external_requests import get_request_headers, get_request_timeout
from app.models.exceptions import ContentFetchingException
from app.models.galnet import GalnetArticle
from app.models.language import Language


class GalnetService:
    """Main class for the Galnet service."""

    def _get_picture_for_article(
        self, article_title: str, website_api_content: List[Dict[str, Any]]
    ) -> Optional[str]:
        website_item = next(
            (x for x in website_api_content if x["title"] == article_title), None
        )
        if website_item is None:
            return None

        base_url = "http://hosting.zaonce.net/elite-dangerous/galnet/"
        picture_name = website_item["image"]
        if "," in picture_name:
            picture_name = picture_name.split(",")[0]

        return f"{base_url}{picture_name}.png"

    async def get_articles(self, language: Language) -> List[GalnetArticle]:
        """Get the latest Galnet articles.

        :raises ContentFetchingException: Unable to retrieve the articles
        """
        url = "https://rss-bridge.9cw.eu/?action=display&bridge=EliteDangerousGalnet&format=Json"
        if language != Language.ENGLISH:
            url += f"&language={language.value}"

        rss_res = httpx.get(
            url, headers=get_request_headers(), timeout=get_request_timeout()
        )
        if rss_res.status_code != 200:
            raise ContentFetchingException()

        articles = rss_res.json()

        # Get official website JSON for the pictures
        website_api_content: List[Dict[str, Any]] = []
        website_api_req = httpx.get(
            "https://elitedangerous-website-backend-production.elitedangerous.com/api/galnet?_format=json",
            headers=get_request_headers(),
            timeout=get_request_timeout(),
        )
        if website_api_req.status_code == 200:
            # only first 15 elements like other source used
            website_api_content = website_api_req.json()[:15]

        # Build response
        response_list: List[GalnetArticle] = []
        for item in articles["items"]:
            title = item["title"]
            new_item = GalnetArticle(
                content=item["content_html"]
                if "content_html" in item
                else "No description",
                uri=item["url"],
                title=title,
                published_date=pendulum.parse(item["date_modified"]),  # type: ignore
                picture=self._get_picture_for_article(title, website_api_content),
            )
            response_list.append(new_item)

        return response_list
