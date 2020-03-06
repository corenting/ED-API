from flask import Blueprint, redirect, jsonify

from api.extensions.database import db
from api.helpers.response import error_response
from common.edsm import get_system
from common.space import distance_between_systems
from models.database import Ship, StationShipLink, System
from requests.api import request

ship_finder_bp = Blueprint("ship_finder", __name__)


@ship_finder_bp.route("/")
def flask_find_ship():
    # Get params
    system_name = request.args.get("referenceSystem")
    ship_name = request.args.get("ship")

    # First, try to get ref system from local db
    reference_system = (
        db.session.query(System).filter(System.name == system_name).first()
    )
    # Else, try to get it from EDSM API
    if reference_system is None:
        reference_system = get_system(system_name)
    if reference_system is None:
        return error_response(f"{system_name} system not found")

    ship_id = db.session.query(Ship).filter(Ship.name.ilike(f"%{ship_name}%")).first()
    if ship_id is None:
        return error_response(f"Ship {ship_name} not found")
    ship_id = ship_id.id

    stations = (
        db.session.query(StationShipLink)
        .filter(
            StationShipLink.ship_id == ship_id
            and reference_system.x - 25
            <= StationShipLink.station.system.x
            <= reference_system.x + 25
            and reference_system.y - 25
            <= StationShipLink.station.system.y
            <= reference_system.y + 25
            and reference_system.z - 25
            <= StationShipLink.station.system.z
            <= reference_system.z + 25
        )
        .all()
    )
    ret_list = [
        {
            "station": s.station,
            "distance": distance_between_systems(reference_system, s.station.system),
        }
        for s in stations
    ]
    ret_list.sort(key=lambda o: o["distance"])
    return jsonify(ret_list[:150])
