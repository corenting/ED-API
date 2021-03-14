from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl


class GalnetArticle(BaseModel):
    content: str
    picture: Optional[HttpUrl]
    title: str
    uri: HttpUrl
    published_date: date
