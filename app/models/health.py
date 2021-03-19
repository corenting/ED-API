from pydantic.dataclasses import dataclass


@dataclass
class Version:
    version: str
