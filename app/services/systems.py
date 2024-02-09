import math
from datetime import UTC, datetime
from typing import Any

import httpx
from dateutil.parser import parse

from app.helpers.httpx import get_aynsc_httpx_client
from app.models.exceptions import ContentFetchingError, SystemNotFoundError
from app.models.stations import Station
from app.models.systems import (
    System,
    SystemDetails,
    SystemDetailsFaction,
    SystemFactionHistory,
    SystemFactionHistoryDetails,
    SystemsDistance,
)
from app.services.helpers.fleet_carriers import is_fleet_carrier
from app.services.helpers.settlements import is_settlement
from app.services.helpers.spansh import (
    SpanshStationService,
    get_station_max_landing_pad_size,
    station_has_service,
)


class SystemsService:
    """Main class for the systems service."""

    MIN_LENGTH_FOR_TYPEHEAD = 3
    FUELRATS_TYPEAHEAD_URL = "https://system.api.fuelrats.com/typeahead"
    SPANSH_STATIONS_SEARCH_URL = "https://spansh.co.uk/api/stations/search"
    SPANSH_SYSTEMS_SEARCH_URL = "https://spansh.co.uk/api/systems/search"
    EDSM_SYSTEM_FACTIONS_URL = "https://www.edsm.net/api-system-v1/factions"

    async def get_systems_typeahead(self, input_text: str) -> list[str]:
        """Get systems names for autocomplete.

        :raises ContentFetchingException: Unable to retrieve the data
        """
        # If less than 3 chars return nothing
        if len(input_text) < self.MIN_LENGTH_FOR_TYPEHEAD:
            return []

        url = f"{self.FUELRATS_TYPEAHEAD_URL}?term={input_text}"
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(url)
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        data = api_response.json()
        if data is None:
            data = []
        return data

    async def _get_system(self, system_name: str) -> System:
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(
                    f"https://www.edsm.net/api-v1/system?systemName={system_name}&showCoordinates=1&showPermit=1"
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        json_content = api_response.json()

        if json_content is None or len(json_content) == 0:
            raise SystemNotFoundError(system_name)

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
                api_response = await client.post(
                    self.SPANSH_SYSTEMS_SEARCH_URL,
                    json={
                        "filters": {"name": {"value": system_name}},
                        "sort": [{"distance": {"direction": "asc"}}],
                        "size": 1,
                        "page": 0,
                    },
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        json_content = api_response.json()

        if json_content is None or len(json_content["results"]) == 0:
            raise SystemNotFoundError(system_name)

        result = json_content["results"][0]

        try:
            factions = await self.__get_systems_factions_details(system_name)
        except ContentFetchingError:
            factions = []

        return SystemDetails(
            allegiance=result.get("allegiance"),
            controlling_faction_state=result.get("controlling_minor_faction_state"),
            controlling_faction=result.get("controlling_minor_faction"),
            government=result.get("government"),
            name=result["name"],
            permit_required=result["needs_permit"],
            population=result.get("population"),
            power_state=result.get("power_state"),
            power=result["power"][0] if len(result.get("power", [])) > 0 else None,
            primary_economy=result.get("primary_economy"),
            secondary_economy=result.get("secondary_economy"),
            security=result.get("security"),
            state=result.get("state"),
            x=result["x"],
            y=result["y"],
            z=result["z"],
            factions=factions,
        )

    async def get_system_stations(self, system_name: str) -> list[Station]:
        """Get system stations.

        :raises ContentFetchingException: Unable to retrieve the data
        :raises SystemNotFoundException: Unable to retrieve the system
        """
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.post(
                    self.SPANSH_STATIONS_SEARCH_URL,
                    json={
                        "filters": {"system_name": {"value": system_name}},
                        "sort": [{"distance": {"direction": "asc"}}],
                        "size": 200,
                        "page": 0,
                    },
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        # We need the system too
        system = await self.get_system_details(system_name)

        # Check that the system has stations
        json_content = api_response.json()
        if json_content is None or len(json_content["results"]) == 0:
            return []

        stations: list[Station] = []
        for item in json_content["results"]:
            # Skip station if unknown type
            # This allows to skip settlements with low informations
            if "type" not in item:
                continue

            station_landing_pad_size = get_station_max_landing_pad_size(item)
            stations.append(
                Station(
                    distance_to_arrival=item["distance_to_arrival"],
                    has_blackmarket=station_has_service(
                        item, SpanshStationService.BLACK_MARKET
                    ),
                    has_docking=station_has_service(item, SpanshStationService.DOCK),
                    has_market=item.get("has_market", False),
                    has_missions=station_has_service(
                        item, SpanshStationService.MISSIONS
                    ),
                    has_outfitting=item.get("has_outfitting", False),
                    has_restock=station_has_service(item, SpanshStationService.RESTOCK),
                    has_refuel=station_has_service(item, SpanshStationService.REFUEL),
                    has_repair=station_has_service(item, SpanshStationService.REPAIR),
                    has_shipyard=item.get("has_shipyard", False),
                    has_universal_cartographics=station_has_service(
                        item, SpanshStationService.UNIVERSAL_CARTOGRAPHICS
                    ),
                    is_fleet_carrier=is_fleet_carrier(
                        item.get("controlling_minor_faction")
                    ),
                    is_planetary=item["is_planetary"],
                    is_settlement=is_settlement(item["type"]),
                    last_market_update=(
                        parse(item["market_updated_at"])
                        if item.get("market_updated_at")
                        else None
                    ),
                    last_outfitting_update=(
                        parse(item["outfitting_updated_at"])
                        if item.get("outfitting_updated_at")
                        else None
                    ),
                    last_shipyard_update=(
                        parse(item["shipyard_updated_at"])
                        if item.get("shipyard_updated_at")
                        else None
                    ),
                    max_landing_pad_size=station_landing_pad_size,
                    name=item["name"],
                    system_name=item["system_name"],
                    system_permit_required=system.permit_required,
                    type=item["type"],
                )
            )

        return stations

    async def __get_systems_factions_details(
        self, system_name: str
    ) -> list[SystemDetailsFaction]:
        """Get system factions details."""
        async with get_aynsc_httpx_client() as client:
            try:
                api_response = await client.get(
                    f"{self.EDSM_SYSTEM_FACTIONS_URL}?systemName={system_name}"
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        json_content = api_response.json()

        # Check result is not empty
        if json_content is None or len(json_content.get("factions", [])) == 0:
            return []

        factions = []
        for item in json_content["factions"]:
            new_faction = SystemDetailsFaction(
                allegiance=item["allegiance"],
                happiness=item["happiness"],
                influence=item["influence"],
                name=item["name"],
                state=item["state"],
                government=item["government"],
                is_player_faction=item["isPlayer"],
                updated_at=datetime.fromtimestamp(item["lastUpdate"], tz=UTC),
            )
            factions.append(new_faction)
        return factions

    def _get_system_faction_history(
        self, faction: dict[str, Any]
    ) -> list[SystemFactionHistoryDetails]:
        ret_items = []

        # Add history
        for attribute, value in faction["influenceHistory"].items():
            # State history
            state_history_value = None
            if not isinstance(faction["stateHistory"], list):
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
                    updated_at=datetime.fromtimestamp(int(attribute), tz=UTC),
                )
            )
        ret_items.sort(key=lambda o: o.updated_at)

        # Add current state
        ret_items.append(
            SystemFactionHistoryDetails(
                influence=faction["influence"],
                state=faction["state"],
                updated_at=datetime.fromtimestamp(int(faction["lastUpdate"]), tz=UTC),
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
                raise ContentFetchingError() from e

        json_content = api_response.json()

        if json_content is None or len(json_content) == 0:
            raise SystemNotFoundError(system_name)

        return [
            SystemFactionHistory(
                faction_name=faction["name"],
                history=self._get_system_faction_history(faction),
            )
            for faction in json_content["factions"]
        ]
