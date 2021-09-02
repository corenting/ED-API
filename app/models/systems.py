from pydantic.dataclasses import dataclass


@dataclass
class SystemsDistance:
    ly_distance: float
    permit_required_for_first_system: bool
    permit_required_for_second_system: bool


@dataclass
class SystemDetails:
    name: str
    x: float
    y: float
    z: float
    permit_required: bool
