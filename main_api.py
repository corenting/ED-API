#!/usr/bin/env python3

from flask import Flask, jsonify

from api.commodities.main import commodities_bp
from api.community_goals.main import community_goals_bp
from api.database import register_db, db
from api.engineering.main import engineering_bp
from api.news.main import news_bp
from api.galnet.main import galnet_bp
from api.helpers.json_encoder import CustomJsonEncoder
from api.misc.main import misc_bp
from api.ships.main import ships_bp
from api.system.main import system_bp
from config import DEBUG_MODE, DB_URI
from models.internal.api_error import ApiError

# App config
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


@app.errorhandler(ApiError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    db.create_all()
    if DEBUG_MODE:
        app.run(host="0.0.0.0", debug=True)
    else:
        app.run(host="0.0.0.0")
