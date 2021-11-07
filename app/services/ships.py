import httpx
import pendulum

from app.constants import STATIC_PATH
from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingException
from app.models.ships import ShipModel, StationSellingShip
from app.models.stations import StationLandingPadSize


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
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.post(
                    self.SHIPS_SEARCH_ENDPOINT,
                    json={
                        "filters": {"ships": {"value": [ship_model.values[0]]}},
                        "sort": [{"distance": {"direction": "asc"}}],
                        "size": 15,
                        "page": 0,
                        "reference_system": reference_system,
                    },
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        stations = api_response.json()["results"]

        return [
            StationSellingShip(
                distance_from_reference_system=item["distance"],
                distance_to_arrival=item["distance_to_arrival"],
                max_landing_pad_size=StationLandingPadSize.LARGE
                if item["has_large_pad"]
                else StationLandingPadSize.MEDIUM
                if item["medium_pads"] > 0
                else StationLandingPadSize.SMALL,
                name=item["name"],
                shipyard_updated_at=pendulum.parse(item["shipyard_updated_at"]),  # type: ignore
                system_name=item["system_name"],
                is_planetary=item["is_planetary"],
                is_fleet_carrier=item["controlling_minor_faction"] == "FleetCarrier",
            )
            for item in stations
        ]
