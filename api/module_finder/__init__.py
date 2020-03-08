from flask import Blueprint, jsonify
from requests.api import request

from api.extensions.database import db
from api.helpers.response import error_response
from common.edsm import get_system
from common.space import distance_between_systems
from models.database import StationModuleLink, System

module_finder_bp = Blueprint("module_finder", __name__)


@module_finder_bp.route("/")
def flask_find_module():
    # Get params
    system_name = request.args.get("referenceSystem")
    module_id = request.args.get("moduleId")

    # First, try to get ref system from local db
    reference_system = (
        db.session.query(System).filter(System.name == system_name).first()
    )
    # Else, try to get it from EDSM API
    if reference_system is None:
        reference_system = get_system(system_name)
    if reference_system is None:
        return error_response(f"{system_name} system not found")

    stations = (
        db.session.query(StationModuleLink)
        .filter(
            StationModuleLink.module_id == module_id
            and reference_system.x - 25
            <= StationModuleLink.station.system.x
            <= reference_system.x + 25
            and reference_system.y - 25
            <= StationModuleLink.station.system.y
            <= reference_system.y + 25
            and reference_system.z - 25
            <= StationModuleLink.station.system.z
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
