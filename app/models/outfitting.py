from pydantic.dataclasses import dataclass


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
