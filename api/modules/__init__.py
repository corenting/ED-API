import arrow
from flask import Blueprint, request, jsonify
from sqlalchemy import text, desc, asc, and_

from api.extensions.database import db
from api.helpers.response import error_response
from common.market import price_difference
from models.database import Commodity, CommodityPrice, Module

modules_bp = Blueprint("modules", __name__)


@modules_bp.route("/")
def flask_get_modules():
    """Return the list of all modules
    ---
    tags:
      - Modules
    responses:
      200:
        description: A list of modules
    """
    db_list = db.session.query(Module).all()
    return jsonify(db_list)
