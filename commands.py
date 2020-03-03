from flask.cli import AppGroup
from sqlalchemy import create_engine

from community_goals.watcher import launch_cg_watch
from config import DB_URI
from eddn.main import listen_to_eddn
from external_import import blueprints, system_stations, commodities
from models.database import get_session

import_cli = AppGroup("import", short_help="Run database imports.")
community_goals_cli = AppGroup(
    "community_goals", short_help="Run community goals scripts."
)
eddn_cli = AppGroup("eddn", short_help="Run EDDN scripts.")


@import_cli.command("all")
def import_all():
    """
    Launch a database import for all data
    """
    db_engine = create_engine(DB_URI)
    with get_session(db_engine) as session:
        blueprints.import_blueprints(session)
        commodities.import_commodities(session)
        system_stations.import_systems_and_stations(session)


@community_goals_cli.command("watch")
def community_goals_watch():
    launch_cg_watch()


@eddn_cli.command("listener")
def eddn_listener():
    listen_to_eddn()
