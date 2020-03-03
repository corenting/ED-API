import logging

from flask import Flask

from api.commodities.main import commodities_bp
from api.community_goals.main import community_goals_bp
from api.database import register_db, db
from api.engineering.main import engineering_bp
from api.extensions.error_handler import handle_invalid_usage
from api.galnet.main import galnet_bp
from api.helpers.json_encoder import CustomJsonEncoder
from api.misc.main import misc_bp
from api.news.main import news_bp
from api.ships.main import ships_bp
from api.system.main import system_bp
from commands import import_cli, community_goals_cli, eddn_cli
from config import DEBUG_MODE, DB_URI, LOG_LEVEL
from models.exceptions.api_exception import ApiError


def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJsonEncoder
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    register_db(app)

    # Blueprints
    app.register_blueprint(community_goals_bp, url_prefix="/community_goals")
    app.register_blueprint(commodities_bp, url_prefix="/commodities")
    app.register_blueprint(engineering_bp, url_prefix="/engineering")
    app.register_blueprint(ships_bp, url_prefix="/ships")
    app.register_blueprint(system_bp, url_prefix="/system")
    app.register_blueprint(galnet_bp, url_prefix="/galnet")
    app.register_blueprint(news_bp, url_prefix="/news")
    app.register_blueprint(misc_bp, url_prefix="/")

    app.register_error_handler(ApiError.status_code, handle_invalid_usage)

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
