from enum import Enum
from typing import Optional

from pendulum.datetime import DateTime
from pydantic.dataclasses import dataclass


class StationLandingPadSize(Enum):
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"


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
    is_fleet_carrier: bool
    last_market_update: Optional[DateTime]
    last_outfitting_update: Optional[DateTime]
    last_shipyard_update: Optional[DateTime]
    max_landing_pad_size: Optional[StationLandingPadSize]
    name: str
    type: str
