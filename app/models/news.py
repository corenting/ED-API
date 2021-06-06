from pendulum.date import Date
from pydantic.dataclasses import dataclass


@dataclass
class NewsArticle:
    content: str
    title: str
    uri: str
    published_date: Date
