from flask import Blueprint, redirect

from api.database import db
from api.helpers.response import error_response, get_response
from common.edsm import get_system_from_edsm
from common.space import distance_between_systems
from models.database import System

misc_bp = Blueprint("misc", __name__)


@misc_bp.route("/")
def flask_hello():
    return "ED-API is running."


@misc_bp.route("/distance/<first>/<second>")
def flask_get_distance(first, second):
    return get_response(get_distance(first, second))


# Old redirect
@misc_bp.route("/v2/community_goals/")
def flask_get_community_goals_v2_old():
    return redirect('community_goals/v2/', 301)


# Old redirect
@misc_bp.route("/<system>/stations/ships/<ship>")
def flask_get_stations_selling_ship_old(system, ship):
    return redirect('system/{}/stations/ships/{}'.format(system, ship), 301)


# Old redirect
@misc_bp.route("/<system>/stations/commodities/<commodity>")
def flask_get_stations_selling_commodity_old(system, commodity):
    return redirect('system/{}/stations/commodities/{}'.format(system, commodity), 301)


def get_distance(first, second):
    # First, try to get systems from local db
    first_system = db.session.query(System).filter(System.name == first).first()
    second_system = db.session.query(System).filter(System.name == second).first()

    # Else, try to get them from EDSM API
    if first_system is None:
        first_system = get_system_from_edsm(first)
    if second_system is None:
        second_system = get_system_from_edsm(second)

    if first_system is None:
        return error_response(first + ' system not found')
    if second_system is None:
        return error_response(second + ' system not found')

    return {
        'from': first_system,
        'to': second_system,
        'distance': distance_between_systems(first_system, second_system)
    }
