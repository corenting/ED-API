from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker

from app.config import DATABASE_URI

engine = create_engine(DATABASE_URI, future=True)
Session = sessionmaker(engine)


class Base(MappedAsDataclass, DeclarativeBase):
    pass
