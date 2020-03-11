import logging
from commands import community_goals_cli, eddn_cli, import_cli

from flasgger import Swagger
from flask import Flask

from api.commodities import commodities_bp
from api.commodity_finder import commodity_finder_bp
from api.community_goals import community_goals_bp
from api.distance_calculator import distance_calculator_bp
from api.engineering import engineering_bp
from api.extensions.database import db, register_db
from api.extensions.error_handler import register_error_handler
from api.extensions.json_encoder import CustomJsonEncoder
from api.galnet import galnet_bp
from api.module_finder import module_finder_bp
from api.news import news_bp
from api.ship_finder import ship_finder_bp
from api.ships import ships_bp
from api.systems import systems_bp
from config import APP_VERSION, DB_URI, DEBUG_MODE, LOG_LEVEL


def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJsonEncoder
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    register_db(app)

    # Swagger
    app.config["SWAGGER"] = {
        "title": "ED-API",
        "description": "An API for Elite Dangerous",
        "uiversion": 3,
        "termsOfService": None,
        "version": APP_VERSION,
    }
    Swagger(app)

    # Blueprints
    app.register_blueprint(community_goals_bp, url_prefix="/community_goals")
    app.register_blueprint(commodities_bp, url_prefix="/commodities")
    app.register_blueprint(engineering_bp, url_prefix="/engineering")
    app.register_blueprint(ships_bp, url_prefix="/ships")
    app.register_blueprint(systems_bp, url_prefix="/system")
    app.register_blueprint(galnet_bp, url_prefix="/galnet")
    app.register_blueprint(news_bp, url_prefix="/news")
    app.register_blueprint(distance_calculator_bp, url_prefix="/distance_calculator")
    app.register_blueprint(ship_finder_bp, url_prefix="/ship_finder")
    app.register_blueprint(module_finder_bp, url_prefix="/module_finder")
    app.register_blueprint(commodity_finder_bp, url_prefix="/commodity_finder")

    register_error_handler(app)

    # Commands
    app.cli.add_command(import_cli)
    app.cli.add_command(community_goals_cli)
    app.cli.add_command(eddn_cli)

    # Logging

    logging.basicConfig(
        level=LOG_LEVEL, format="[%(levelname)s] - %(asctime)s - %(message)s"
    )
    if not DEBUG_MODE:
        handler = logging.handlers.SysLogHandler(address="/dev/log")
        logging.getLogger().addHandler(handler)

    return app


def main():
    app = create_app()
    db.create_all()
    if DEBUG_MODE:
        app.run(host="0.0.0.0", debug=True)
    else:
        app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
