from pendulum.datetime import DateTime
from pydantic.dataclasses import dataclass


@dataclass
class CommunityGoal:
    contributors: int
    current_tier: int
    description: str
    end_date: DateTime
    id: int
    last_update: DateTime
    objective: str
    ongoing: bool
    reward: str
    station: str
    system: str
    max_tier: int
    title: str
