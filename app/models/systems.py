from datetime import datetime

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
    allegiance: str | None
    controlling_faction_state: str | None
    controlling_faction: str | None
    government: str | None
    name: str
    permit_required: bool
    population: int | None
    power_state: str | None
    power: str | None
    primary_economy: str | None
    secondary_economy: str | None
    security: str | None
    state: str | None
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
