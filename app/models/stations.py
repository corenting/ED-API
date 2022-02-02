from enum import Enum
from functools import total_ordering
from typing import Any, Optional

from pendulum.datetime import DateTime
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
    has_outfitting: bool
    has_rearm: bool
    has_refuel: bool
    has_repair: bool
    has_shipyard: bool
    is_planetary: bool
    last_market_update: Optional[DateTime]
    last_outfitting_update: Optional[DateTime]
    last_shipyard_update: Optional[DateTime]
    max_landing_pad_size: Optional[StationLandingPadSize]
    name: str
    type: str
    system_name: str
    system_permit_required: bool
