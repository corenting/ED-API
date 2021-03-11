from pydantic.main import BaseModel


class Version(BaseModel):
    version: str
