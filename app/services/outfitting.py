import csv
import datetime
from typing import Any

import httpx
from dateutil.parser import parse

from app.constants import DATA_PATH, SPANSH_STATIONS_SEARCH_URL
from app.helpers.httpx import get_async_httpx_client
from app.models.exceptions import ContentFetchingError, OutfittingNotFoundError
from app.models.outfitting import Outfitting, StationWithOutfittingDetails
from app.models.stations import StationLandingPadSize
from app.services.helpers.fleet_carriers import is_fleet_carrier
from app.services.helpers.settlements import is_settlement
from app.services.helpers.spansh import get_station_max_landing_pad_size


class OutfittingService:
    def __init__(self) -> None:
        self.outfittings = self._parse_outfitting_csv()

    def _parse_outfitting_csv(self) -> list[Outfitting]:
        items: list[Outfitting] = []
        with open(DATA_PATH + "/outfitting.csv") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            items.extend(
                Outfitting(
                    id=int(row["id"]),
                    symbol=row["symbol"],
                    category=row["category"],
                    name=row["name"],
                    mount=row["mount"],
                    guidance=row["guidance"],
                    ship=row["ship"],
                    outfitting_class=int(row["class"]),
                    outfitting_rating=row["rating"],
                    display_name="",
                )
                for row in csv_reader
            )

        # Compute display names
        for item in items:
            item.display_name = self._get_display_name_for_outfitting(item)

        return items

    def _get_display_name_for_outfitting(self, outfitting: Outfitting) -> str:
        """
        Get a display name for the specified outfitting item.
        """
        name = ""
        if outfitting.outfitting_class:
            name += f"[{outfitting.outfitting_class}{outfitting.outfitting_rating}] "

        name += outfitting.name
        if outfitting.mount:
            guidance = f"{outfitting.guidance}, " if outfitting.guidance else ""
            name += f" ({guidance}{outfitting.mount})"
        elif outfitting.ship:
            name += f" ({outfitting.ship})"

        return name

    def get_outfitting_typeahead(self, input_text: str) -> list[str]:
        """
        Return a list of outfitting matching the input
        """
        return [
            item.display_name
            for item in self.outfittings
            if input_text.lower().strip() in item.display_name.lower()
        ]

    def _find_outfitting_generate_request_body(
        self,
        reference_system: str,
        outfitting: Outfitting,
        max_age_days: int,
    ) -> dict[str, Any]:
        now = datetime.datetime.now(tz=datetime.UTC).isoformat()
        max_age = (
            datetime.datetime.now(tz=datetime.UTC)
            - datetime.timedelta(days=max_age_days)
        ).isoformat()

        body = {
            "filters": {
                "modules": [
                    {
                        "name": [outfitting.name],
                        "class": [str(outfitting.outfitting_class)],
                        "rating": [outfitting.outfitting_rating],
                    }
                ],
                "outfitting_updated_at": {"comparison": "<=>", "value": [max_age, now]},
            },
            "sort": [
                {"distance": {"direction": "asc"}},
                {"distance_to_arrival": {"direction": "asc"}},
            ],
            "size": 50,
            "page": 0,
            "reference_system": reference_system,
        }

        return body

    def _map_spansh_stations_to_model(
        self,
        api_response: httpx.Response,
        min_landing_pad_size: StationLandingPadSize,
    ) -> list[StationWithOutfittingDetails]:
        res: list[StationWithOutfittingDetails] = []
        for item in api_response.json()["results"]:
            station_landing_pad_size = get_station_max_landing_pad_size(item)

            if station_landing_pad_size > min_landing_pad_size:
                continue

            res.append(
                StationWithOutfittingDetails(
                    distance_from_reference_system=item["distance"],
                    distance_to_arrival=item["distance_to_arrival"],
                    is_planetary=item["is_planetary"],
                    last_outfitting_update=parse(item["outfitting_updated_at"])
                    if item.get("outfitting_updated_at")
                    else None,  # type: ignore
                    max_landing_pad_size=station_landing_pad_size,
                    name=item["name"],
                    system_name=item["system_name"],
                    type=item.get("type", "Unknown"),
                    is_fleet_carrier=is_fleet_carrier(
                        item.get("controlling_minor_faction")
                    ),
                    is_settlement=is_settlement(item.get("type")),
                )
            )

        return res

    async def find_outfitting(
        self,
        reference_system: str,
        outfitting_name: str,
        min_landing_pad_size: StationLandingPadSize,
        max_age_days: int,
    ) -> list[StationWithOutfittingDetails]:
        """Get stations buying or selling a specific outfitting near a reference system."""
        # Get the searched outfitting
        outfitting = next(
            (item for item in self.outfittings if item.display_name == outfitting_name),
            None,
        )
        if outfitting is None:
            raise OutfittingNotFoundError(outfitting_name)

        async with get_async_httpx_client() as client:
            try:
                api_response = await client.post(
                    SPANSH_STATIONS_SEARCH_URL,
                    json=self._find_outfitting_generate_request_body(
                        reference_system, outfitting, max_age_days
                    ),
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        return self._map_spansh_stations_to_model(api_response, min_landing_pad_size)
