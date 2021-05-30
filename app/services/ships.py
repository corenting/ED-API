from typing import List, Optional

from app.models.ships import Ship
from app.services.constants import SHIPS_FRONTIER_API_MAPPING


class ShipsService:
    """Main class for the ships service."""

    async def get_ship_model_informations(self, ship_model: str) -> Ship:
        """Get informations about a specific ship model."""
        # FIXME
        return Ship(model="FIXME", picture_url="FIXME", description="FIXME")

    async def get_all_ships(self) -> List[Ship]:
        """Get all ships."""
        # FIXME
        return []

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
