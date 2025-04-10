import datetime
from enum import Enum
from typing import Any

from app.models.stations import StationLandingPadSize


class SpanshStationService(Enum):
    BLACK_MARKET = "black market"
    DOCK = "dock"
    MISSIONS = "missions"
    REFUEL = "refuel"
    REPAIR = "repair"
    RESTOCK = "restock"
    UNIVERSAL_CARTOGRAPHICS = "universal cartographics"


def get_station_max_landing_pad_size(station: dict[str, Any]) -> StationLandingPadSize:
    """Get max landing pad size of a station."""
    if station["has_large_pad"]:
        return StationLandingPadSize.LARGE
    if station.get("medium_pads", 0) > 0:
        return StationLandingPadSize.MEDIUM
    return StationLandingPadSize.SMALL


def station_has_service(
    station: dict[str, Any], service_to_find: SpanshStationService
) -> bool:
    """Check if a station has a service."""
    return (
        next(
            (
                service
                for service in station["services"]
                if service["name"].lower() == service_to_find.value.lower()
            ),
            None,
        )
        is not None
    )


def get_request_body_common_filters() -> dict[str, Any]:
    """
    Get common filters used for requesting Spansh API (sorting, page size etc.)
    """
    return {
        "sort": [
            {"distance": {"direction": "asc"}},
            {"distance_to_arrival": {"direction": "asc"}},
        ],
        "size": 50,
        "page": 0,
    }


def get_max_age_values_for_request_body(max_age_days: int) -> dict[str, Any]:
    """
    Get the dict filter to use to express that a datetime field in the request body
    should have a max age of the given number of days
    """
    now = datetime.datetime.now(tz=datetime.UTC).isoformat()
    max_age = (
        datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=max_age_days)
    ).isoformat()

    return {"comparison": "<=>", "value": [max_age, now]}


def get_formatted_reference_system(system: str) -> str:
    """
    Format the given reference system name: keep as-is if the first letter is uppercase (as
    it probably come from the autocomplete), else make it a title to try to at least fix
    simple cases instead of returning an error.
    """
    formatted_system = system.strip()
    return (
        formatted_system.title() if formatted_system[0].islower() else formatted_system
    )
