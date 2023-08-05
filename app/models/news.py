from datetime import date

from pydantic.dataclasses import dataclass


@dataclass
class NewsArticle:
    content: str
    title: str
    uri: str
    published_date: date
    picture: str | None = None
