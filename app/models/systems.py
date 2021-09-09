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
