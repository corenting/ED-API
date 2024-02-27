from pydantic.dataclasses import dataclass


@dataclass
class GameServerHealth:
    status: str
