from enum import Enum
from typing import Any, Optional

from app.models.stations import StationLandingPadSize


class SpanshStationService(Enum):
    BLACK_MARKET = "black market"
    DOCK = "dock"
    MISSIONS = "missions"
    REFUEL = "refuel"
    REPAIR = "repair"
    RESTOCK = "restock"
    UNIVERSAL_CARTOGRAPHICS = "universal cartographics"


def get_station_max_landing_pad_size(
    station: dict[str, Any]
) -> Optional[StationLandingPadSize]:
    """Get max landing pad size of a station."""
    if station["has_large_pad"]:
        return StationLandingPadSize.LARGE
    if station.get("medium_pads", 0) > 0:
        return StationLandingPadSize.MEDIUM
    if station.get("small_pads", 0) > 0:
        return StationLandingPadSize.SMALL
    return None


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
