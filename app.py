import logging

from flask import Flask

from api.commodities import commodities_bp
from api.community_goals import community_goals_bp
from api.extensions.database import register_db, db
from api.engineering import engineering_bp
from api.extensions.error_handler import handle_invalid_usage, register_error_handler
from api.galnet import galnet_bp
from api.extensions.json_encoder import CustomJsonEncoder
from api.distance_calculator import distance_calculator_bp
from api.news import news_bp
from api.ships import ships_bp
from api.systems import systems_bp
from commands import import_cli, community_goals_cli, eddn_cli
from config import DEBUG_MODE, DB_URI, LOG_LEVEL
from models.exceptions.api_exception import ApiException
from flasgger import Swagger


def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJsonEncoder
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    register_db(app)

    # Swagger
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

    register_error_handler(app)

    # Commands
    app.cli.add_command(import_cli)
    app.cli.add_command(community_goals_cli)
    app.cli.add_command(eddn_cli)

    # Logging
    logging.basicConfig(level=LOG_LEVEL)

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
