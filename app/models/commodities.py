from pydantic.dataclasses import dataclass


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
