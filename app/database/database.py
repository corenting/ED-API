from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URI

engine = create_engine(DATABASE_URI, future=True)
Session = sessionmaker(engine)

Base = declarative_base()
