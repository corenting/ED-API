import math
from typing import Any

import httpx
import pendulum

from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingException, SystemNotFoundException
from app.models.stations import Station, StationLandingPadSize
from app.models.systems import (
    System,
    SystemDetails,
    SystemFactionHistory,
    SystemFactionHistoryDetails,
    SystemsDistance,
)


class SystemsService:
    """Main class for the systems service."""

    TYPEAHEAD_SERVICE_URL = "https://system.api.fuelrats.com/typeahead"

    async def get_systems_typeahead(self, input_text: str) -> list[str]:
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

    async def _get_system(self, system_name: str) -> System:
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

        return System(
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
        :raises SystemNotFoundException: Unable to retrieve the system
        """
        first_system = await self._get_system(first_system_name)
        second_system = await self._get_system(second_system_name)

        distance = math.dist(
            [first_system.x, first_system.y, first_system.z],
            [second_system.x, second_system.y, second_system.z],
        )

        return SystemsDistance(
            distance_in_ly=round(distance, 2),
            first_system=first_system,
            second_system=second_system,
        )

    async def get_system_details(self, system_name: str) -> SystemDetails:
        """Get system details.

        :raises ContentFetchingException: Unable to retrieve the data
        :raises SystemNotFoundException: Unable to retrieve the system
        """
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(
                    f"https://www.edsm.net/api-v1/system?systemName={system_name}&showCoordinates=1&showPermit=1&showInformation=1"
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        json_content = api_response.json()

        if json_content is None or len(json_content) == 0:
            raise SystemNotFoundException(system_name)

        details = json_content.get("information")
        return SystemDetails(
            name=json_content["name"],
            x=json_content["coords"]["x"],
            y=json_content["coords"]["y"],
            z=json_content["coords"]["z"],
            permit_required=json_content["requirePermit"],
            allegiance=details.get("allegiance"),
            government=details.get("government"),
            controlling_faction=details.get("faction"),
            state=details.get("factionState"),
            population=details.get("population"),
            security=details.get("security"),
            economy=details.get("economy"),
        )

    async def get_system_stations(self, system_name: str) -> list[Station]:
        """Get system stations.

        :raises ContentFetchingException: Unable to retrieve the data
        :raises SystemNotFoundException: Unable to retrieve the system
        """
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(
                    f"https://eddbapi.kodeblox.com/api/v4/stations?systemname={system_name}"
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        json_content = api_response.json()

        if json_content is None or len(json_content["docs"]) == 0:
            raise SystemNotFoundException(system_name)

        stations = []
        for item in json_content["docs"]:

            landing_pad_size = None
            if (
                item.get("max_landing_pad_size") is not None
                and item.get("max_landing_pad_size") != "none"
            ):
                landing_pad_size = StationLandingPadSize(
                    str.upper(item["max_landing_pad_size"])
                )

            stations.append(
                Station(
                    distance_to_arrival=item["distance_to_star"],
                    has_blackmarket=item["has_blackmarket"],
                    has_docking=item["has_docking"],
                    has_market=item["has_market"],
                    has_outfitting=item["has_outfitting"],
                    has_rearm=item["has_rearm"],
                    has_refuel=item["has_refuel"],
                    has_repair=item["has_repair"],
                    has_shipyard=item["has_shipyard"],
                    is_planetary=item["is_planetary"],
                    last_market_update=pendulum.parse(item["market_updated_at"]) if item["market_updated_at"] else None,  # type: ignore
                    last_outfitting_update=pendulum.parse(item["outfitting_updated_at"]) if item.get("outfitting_updated_at") else None,  # type: ignore
                    last_shipyard_update=pendulum.parse(item["shipyard_updated_at"]) if item.get("shipyard_updated_at") else None,  # type: ignore
                    max_landing_pad_size=landing_pad_size,
                    name=item["name"],
                    type=str.capitalize(item["type"]),
                )
            )
        return stations

    def _get_system_faction_history(
        self, faction: dict[str, Any]
    ) -> list[SystemFactionHistoryDetails]:
        ret_items = []

        # Add history
        for attribute, value in faction["influenceHistory"].items():
            # State history
            state_history_value = None
            if type(faction["stateHistory"]) != list:
                state_history_value = next(
                    (y for x, y in faction["stateHistory"].items() if x == attribute),
                    None,
                )

            if state_history_value is None:
                continue

            ret_items.append(
                SystemFactionHistoryDetails(
                    influence=value,
                    state=state_history_value,
                    updated_at=pendulum.from_timestamp(int(attribute)),
                )
            )
        ret_items.sort(key=lambda o: o.updated_at)

        # Add current state
        ret_items.append(
            SystemFactionHistoryDetails(
                influence=faction["influence"],
                state=faction["state"],
                updated_at=pendulum.from_timestamp(int(faction["lastUpdate"])),
            )
        )
        return ret_items

    async def get_system_factions_history(
        self, system_name: str
    ) -> list[SystemFactionHistory]:
        """Get factions history for a specified system.

        :raises ContentFetchingException: Unable to retrieve the data
        :raises SystemNotFoundException: Unable to retrieve the system
        """
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(
                    f"https://www.edsm.net/api-system-v1/factions?systemName={system_name}&showHistory=1"
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingException() from e

        json_content = api_response.json()

        if json_content is None or len(json_content) == 0:
            raise SystemNotFoundException(system_name)

        response = []
        for faction in json_content["factions"]:
            response.append(
                SystemFactionHistory(
                    faction_name=faction["name"],
                    history=self._get_system_faction_history(faction),
                )
            )

        return response
