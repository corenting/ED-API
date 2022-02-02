from enum import Enum
from typing import Optional

from pendulum.datetime import DateTime
from pydantic.dataclasses import dataclass

from app.models.stations import StationLandingPadSize


@dataclass
class Commodity:
    id: int
    name: str
    category: str
    is_rare: bool


@dataclass
class CommodityPrice:
    commodity: Commodity
    inara_id: int
    average_buy_price: int
    average_sell_price: int
    minimum_buy_price: int
    maximum_sell_price: int


class FindCommodityMode(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class StationCommodityDetails:
    distance_from_reference_system: int
    distance_to_arrival: float
    is_fleet_carrier: bool
    is_planetary: bool
    last_market_update: Optional[DateTime]
    max_landing_pad_size: Optional[StationLandingPadSize]
    name: str
    price_percentage_difference: int
    price: int
    quantity: int
    system_name: str
    type: str
