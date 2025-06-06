import httpx
from dateutil.parser import parse

from app.constants import STATIC_PATH
from app.helpers.httpx import get_async_httpx_client
from app.models.exceptions import ContentFetchingError
from app.models.ships import ShipModel, StationSellingShip
from app.models.stations import StationLandingPadSize
from app.services.helpers.fleet_carriers import is_fleet_carrier
from app.services.helpers.settlements import is_settlement
from app.services.helpers.spansh import get_formatted_reference_system


class ShipsService:
    """Main class for the ships service."""

    SHIPS_SEARCH_ENDPOINT = "https://spansh.co.uk/api/stations/search"

    async def get_ship_picture_static_path(self, ship_model: ShipModel) -> str:
        """Get the static path to a ship picture."""
        return f"/{STATIC_PATH}/images/ships/{ship_model.values[1]}.png"

    async def get_ships_typeahead(self, input_text: str) -> list[str]:
        """Get ships names for autocomplete."""
        return [
            item
            for item in ShipModel.get_display_names()
            if item.lower().startswith(input_text.lower())
        ]

    async def get_station_selling_ship(
        self, reference_system: str, ship_model: ShipModel
    ) -> list[StationSellingShip]:
        """Search for a station selling a specific ship.

        :raises ContentFetchingException: Unable to retrieve the articles
        """
        async with get_async_httpx_client() as client:
            try:
                api_response = await client.post(
                    self.SHIPS_SEARCH_ENDPOINT,
                    json={
                        "filters": {"ships": {"value": [ship_model.values[0]]}},
                        "sort": [{"distance": {"direction": "asc"}}],
                        "size": 15,
                        "page": 0,
                        "reference_system": get_formatted_reference_system(
                            reference_system
                        ),
                    },
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        stations = api_response.json()["results"]

        return [
            StationSellingShip(
                distance_from_reference_system=item["distance"],
                distance_to_arrival=item["distance_to_arrival"],
                max_landing_pad_size=(
                    StationLandingPadSize.LARGE
                    if item["has_large_pad"]
                    else (
                        StationLandingPadSize.MEDIUM
                        if item["medium_pads"] > 0
                        else StationLandingPadSize.SMALL
                    )
                ),
                name=item["name"],
                shipyard_updated_at=parse(item["shipyard_updated_at"]),
                system_name=item["system_name"],
                is_planetary=item["is_planetary"],
                is_fleet_carrier=is_fleet_carrier(
                    item.get("controlling_minor_faction")
                ),
                is_settlement=is_settlement(item["type"]),
            )
            for item in stations
        ]
