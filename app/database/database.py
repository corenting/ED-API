from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from sqlalchemy.orm import MappedAsDataclass
from app.config import DATABASE_URI

engine = create_engine(DATABASE_URI, future=True)
Session = sessionmaker(engine)


class Base(MappedAsDataclass, DeclarativeBase):
    pass
