from datetime import datetime
from enum import Enum
from functools import total_ordering
from typing import Any

from pydantic.dataclasses import dataclass


@total_ordering
class StationLandingPadSize(Enum):
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"

    def __lt__(self, other: Any) -> Any:
        """Compare two landing pad sizes."""
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


@dataclass
class Station:
    distance_to_arrival: float
    has_blackmarket: bool
    has_docking: bool
    has_market: bool
    has_missions: bool
    has_outfitting: bool
    has_refuel: bool
    has_repair: bool
    has_restock: bool
    has_shipyard: bool
    has_universal_cartographics: bool
    is_fleet_carrier: bool
    is_planetary: bool
    is_settlement: bool
    last_market_update: datetime | None
    last_outfitting_update: datetime | None
    last_shipyard_update: datetime | None
    max_landing_pad_size: StationLandingPadSize
    name: str
    system_name: str
    system_permit_required: bool
    type: str
