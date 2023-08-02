from datetime import date
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class NewsArticle:
    content: str
    title: str
    uri: str
    published_date: date
    picture: Optional[str] = None
