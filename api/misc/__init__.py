from flask import Blueprint, redirect, jsonify

from api.extensions.database import db
from api.helpers.response import error_response
from common.edsm import get_system
from common.space import distance_between_systems
from models.database import System

misc_bp = Blueprint("misc", __name__)


@misc_bp.route("/")
def flask_hello():
    return "ED-API is running."


@misc_bp.route("/distance/<first>/<second>")
def flask_get_distance(first, second):
    # First, try to get systems from local db
    first_system = db.session.query(System).filter(System.name == first).first()
    second_system = db.session.query(System).filter(System.name == second).first()

    # Else, try to get them from EDSM API
    if first_system is None:
        first_system = get_system(first)
    if second_system is None:
        second_system = get_system(second)

    if first_system is None:
        return error_response(first + " system not found", 400)
    if second_system is None:
        return error_response(second + " system not found", 400)

    return jsonify(
        {
            "from": first_system,
            "to": second_system,
            "distance": distance_between_systems(first_system, second_system),
        }
    )
