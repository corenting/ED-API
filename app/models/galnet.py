from dataclasses import dataclass
from typing import Optional

from pendulum.date import Date


@dataclass
class GalnetArticle:
    content: str
    picture: Optional[str]
    title: str
    uri: str
    published_date: Date
