from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class CommunityGoal:
    contributors: int
    current_tier: int
    description: str
    end_date: datetime
    id: int
    last_update: datetime
    objective: str
    ongoing: bool
    reward: str
    station: str
    system: str
    max_tier: int
    title: str
