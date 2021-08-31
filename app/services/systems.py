from typing import List

import httpx

from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingException
from app.models.systems import SystemsDistance


class SystemsService:
    """Main class for the systems service."""

    TYPEAHEAD_SERVICE_URL = "https://system.api.fuelrats.com/typeahead"

    async def get_systems_typeahead(self, input_text: str) -> List[str]:
        """Get systems names for autocomplete.

        :raises ContentFetchingException: Unable to retrieve the data
        """
        url = f"{self.TYPEAHEAD_SERVICE_URL}?term={input_text}"
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(url)
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        return api_response.json()

    async def get_systems_distance_calculator(
        self, first_system_name: str, second_system_name: str
    ) -> SystemsDistance:
        """Get distance between two specified systems.

        :raises ContentFetchingException: Unable to retrieve the data
        :raises SystemNotFoundException: Unable to retrieve the articles
        """
        # TODO
        pass
