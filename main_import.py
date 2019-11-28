from sqlalchemy import create_engine

from config import DB_URI
from external_import import blueprints, system_stations, commodities
from models.database import get_session

db_engine = create_engine(DB_URI)


def blueprints_import():
    with get_session(db_engine) as session:
        blueprints.import_blueprints(session)


def systems_and_stations_import():
    with get_session(db_engine) as session:
        system_stations.import_systems_and_stations(session)


def commodities_import():
    with get_session(db_engine) as session:
        commodities.import_commodities(session)