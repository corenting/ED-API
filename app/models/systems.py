from typing import Optional

from pendulum.datetime import DateTime
from pydantic.dataclasses import dataclass


@dataclass
class System:
    name: str
    x: float
    y: float
    z: float
    permit_required: bool


@dataclass
class SystemDetails:
    name: str
    x: float
    y: float
    z: float
    permit_required: bool
    allegiance: Optional[str]
    government: Optional[str]
    controlling_faction: Optional[str]
    state: Optional[str]
    population: Optional[int]
    security: Optional[str]
    economy: Optional[str]


@dataclass
class SystemsDistance:
    distance_in_ly: float
    first_system: System
    second_system: System


@dataclass
class SystemFactionHistoryDetails:
    influence: float
    state: str
    updated_at: DateTime


@dataclass
class SystemFactionHistory:
    faction_name: str
    history: list[SystemFactionHistoryDetails]
