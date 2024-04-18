from datetime import datetime

from pydantic.dataclasses import dataclass

from app.models.stations import Station


@dataclass
class Outfitting:
    id: int
    symbol: str
    category: str
    name: str
    mount: str | None
    guidance: str | None
    ship: str | None
    outfitting_class: int
    outfitting_rating: str
    display_name: str


@dataclass
class StationWithOutfittingDetails(Station):
    last_outfitting_update: datetime | None
