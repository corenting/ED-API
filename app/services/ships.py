from typing import List, Optional

from app.helpers.httpx import get_httpx_client
from app.models.exceptions import ContentFetchingException, ShipModelNotFound
from app.models.ships import Ship
from app.services.constants import (
    FRONTIER_WEBSITE_API,
    FRONTIER_WEBSITE_BASE_URL,
    SHIPS_FRONTIER_API_MAPPING,
)


class ShipsService:
    """Main class for the ships service."""

    async def get_ship_model_informations(self, ship_model: str) -> Ship:
        """Get informations about a specific ship model."""
        ships_list = await self.get_all_ships()

        ship = next(
            (x for x in ships_list if x.model.lower() == ship_model.lower()), None
        )
        if ship is None:
            raise ShipModelNotFound()
        return ship

    async def get_all_ships(self) -> List[Ship]:
        """Get all ships."""
        async with get_httpx_client() as client:
            api_res = await client.get(f"{FRONTIER_WEBSITE_API}/ships?_format=json")

        if api_res.status_code != 200:
            raise ContentFetchingException()

        res: List[Ship] = []
        for item in api_res.json():
            ship_model = self._get_ship_model_from_frontier_api_model(item["slug"])
            if ship_model is None:
                continue

            res.append(
                Ship(
                    model=ship_model,
                    picture_url=f"{FRONTIER_WEBSITE_BASE_URL}/{item['threeQuarterImage']}",
                    description=item["body"].replace("<p>", "").replace("</p>", ""),
                )
            )

        return res

    def _get_ship_model_from_frontier_api_model(
        self, internal_value: str
    ) -> Optional[str]:
        """
        Get the display name of a ship model from its internal API value.

        :param internal_value: the value as returned by the API.
        :return: the display name of the ship mode, or None if not found.
        """
        if internal_value in SHIPS_FRONTIER_API_MAPPING:
            return SHIPS_FRONTIER_API_MAPPING[internal_value]
        return None
