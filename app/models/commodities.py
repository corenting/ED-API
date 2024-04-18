from datetime import datetime
from enum import Enum

from pydantic.dataclasses import dataclass

from app.models.stations import Station


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
class StationWithCommodityDetails(Station):
    last_market_update: datetime | None
    price_percentage_difference: int
    price: int
    quantity: int


@dataclass
class BestPricesStations:
    best_stations_to_buy: list[StationWithCommodityDetails]
    best_stations_to_sell: list[StationWithCommodityDetails]
