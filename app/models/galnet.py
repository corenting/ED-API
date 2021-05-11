from pendulum.date import Date
from pydantic.dataclasses import dataclass


@dataclass
class GalnetArticle:
    content: str
    picture: str
    title: str
    uri: str
    published_date: Date
