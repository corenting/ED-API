from pydantic.dataclasses import dataclass


@dataclass
class SystemsDistance:
    ly_distance: int
    permit_required_for_first_system: bool
    permit_required_for_second_system: bool
