from pydantic.dataclasses import dataclass


@dataclass
class SystemDetails:
    name: str
    x: float
    y: float
    z: float
    permit_required: bool


@dataclass
class SystemsDistance:
    distance_in_ly: float
    first_system: SystemDetails
    second_system: SystemDetails
