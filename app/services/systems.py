import math
from typing import List

import httpx

from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingException, SystemNotFoundException
from app.models.systems import SystemDetails, SystemsDistance


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

    async def _get_system_details(self, system_name: str) -> SystemDetails:
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(
                    f"https://www.edsm.net/api-v1/system?systemName={system_name}&showCoordinates=1&showPermit=1"
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        json_content = api_response.json()

        if json_content is None or len(json_content) == 0:
            raise SystemNotFoundException(system_name)

        return SystemDetails(
            name=json_content["name"],
            x=json_content["coords"]["x"],
            y=json_content["coords"]["y"],
            z=json_content["coords"]["z"],
            permit_required=json_content["requirePermit"],
        )

    async def get_systems_distance_calculator(
        self, first_system_name: str, second_system_name: str
    ) -> SystemsDistance:
        """Get distance between two specified systems.

        :raises ContentFetchingException: Unable to retrieve the data
        :raises SystemNotFoundException: Unable to retrieve the articles
        """
        first_system = await self._get_system_details(first_system_name)
        second_system = await self._get_system_details(second_system_name)

        distance = math.dist(
            [first_system.x, first_system.y, first_system.z],
            [second_system.x, second_system.y, second_system.z],
        )

        return SystemsDistance(
            ly_distance=round(distance, 2),
            permit_required_for_first_system=first_system.permit_required,
            permit_required_for_second_system=second_system.permit_required,
        )
