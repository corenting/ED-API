from pydantic.dataclasses import dataclass


@dataclass
class Commodity:
    id: int
    name: str
    category: str
    is_rare: bool
