from flask.cli import AppGroup
from sqlalchemy import create_engine

from community_goals.watcher import launch_cg_watch
from config import DB_URI
from eddn.main import listen_to_eddn
from external_import import blueprints, commodities, market, system_stations
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


@import_cli.command("commodities_prices")
def import_commodities_prices():
    """
    Import latest commodities prices on markets
    """
    market.market_import()


@community_goals_cli.command("watch")
def community_goals_watch():
    """
    Watch and send FCM notifications for community goals updates
    """
    launch_cg_watch()


@eddn_cli.command("listener")
def eddn_listener():
    """
    Launch the EDDN listener to update market prices
    """
    listen_to_eddn()
