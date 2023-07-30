from datetime import datetime
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class System:
    name: str
    x: float
    y: float
    z: float
    permit_required: bool


@dataclass
class SystemDetailsFaction:
    allegiance: str
    government: str
    happiness: str
    influence: float
    is_player_faction: bool
    name: str
    state: str
    updated_at: datetime


@dataclass
class SystemDetails:
    allegiance: Optional[str]
    controlling_faction_state: Optional[str]
    controlling_faction: Optional[str]
    government: Optional[str]
    name: str
    permit_required: bool
    population: Optional[int]
    power_state: Optional[str]
    power: Optional[str]
    primary_economy: Optional[str]
    secondary_economy: Optional[str]
    security: Optional[str]
    state: Optional[str]
    x: float
    y: float
    z: float
    factions: list[SystemDetailsFaction]


@dataclass
class SystemsDistance:
    distance_in_ly: float
    first_system: System
    second_system: System


@dataclass
class SystemFactionHistoryDetails:
    influence: float
    state: str
    updated_at: datetime


@dataclass
class SystemFactionHistory:
    faction_name: str
    history: list[SystemFactionHistoryDetails]
