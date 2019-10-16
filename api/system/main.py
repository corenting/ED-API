import json
from urllib.parse import quote

import arrow
import requests
from flask import Blueprint
from sqlalchemy import and_

from api.database import db
from api.helpers.request import get_requests_headers, request_param
from api.helpers.response import get_response, error_response
from common.edsm import get_factions_from_edsm, get_system_from_edsm
from common.faction import get_faction_state_name, get_faction_history_item
from common.market import price_difference
from common.space import distance_between_systems
from common.station import can_dock_at_station
from common.utils import get_name_or_unknown_from_obj, get_name_or_unknown
from models.database import (
    System,
    Station,
    StationShipLink,
    Ship,
    CommodityPrice,
    Commodity,
)

system_bp = Blueprint("system", __name__)


@system_bp.route("/<system>/stations/ships/<ship>")
def flask_get_stations_selling_ship(system, ship):
    return get_response(get_stations_selling_ship(system, ship))


@system_bp.route("/<system>/stations/commodities/<commodity>")
def flask_get_stations_selling_buying_commodity(system, commodity):
    pad_size = request_param("pad", "S")
    min_stock = request_param("stock", 1)
    selling = request_param("selling", 0)
    min_demand = request_param("demand", 0)
    if min_demand == 1:
        min_demand = 0  # TODO : remove hack after next app update
    return get_response(
        get_stations_selling_buying_commodity(
            system, commodity, min_stock, min_demand, pad_size, selling == 1
        )
    )


@system_bp.route("/<system>")
def flask_get_system_info(system):
    return get_response(get_system_info(system))


@system_bp.route("/<system>/stations")
def flask_get_system_stations(system):
    return get_response(get_system_stations(system))


@system_bp.route("/<system>/history")
def flask_get_system_history(system):
    return get_response(get_system_history(system))


@system_bp.route("/<system>/<station>/details")
def flask_get_station_details(system, station):
    return get_response(get_station_details(system, station))


def get_system_stations(system_name):
    reference_system = (
        db.session.query(System).filter(System.name == system_name).first()
    )
    if reference_system is None:
        return error_response(system_name + " system not found")

    db_stations = (
        db.session.query(Station)
        .filter(Station.system_id == reference_system.id)
        .order_by(Station.distance_to_star)
        .all()
    )
    return db_stations


def get_system_history(system_name):
    # Get history from EDSM
    edsm_factions = get_factions_from_edsm(system_name, include_history=True)

    # For each faction, get history
    factions_history = []
    for faction in edsm_factions["factions"]:
        factions_history.append(
            {
                "name": faction["name"],
                "history": get_faction_history_item(system_name, faction),
            }
        )

    return factions_history


def get_system_info(system_name):
    # First, get system details (bgs)
    sys_url = (
        "https://www.edsm.net/api-v1/systems?showInformation=1&showPermit=1&showCoordinates=1&systemName="
        + quote(system_name)
    )
    sys_req = requests.get(sys_url, headers=get_requests_headers())

    # Check response code
    if sys_req.status_code != 200:
        return error_response(system_name + " system not found")

    sys_body = sys_req.content
    sys_json_list = json.loads(sys_body.decode("utf-8"))
    if len(sys_json_list) == 0:
        return error_response(system_name + " system not found")

    sys_json = sys_json_list[0]
    sys_req.close()

    # Check if information is null in JSON, to replace it with empty object instead of empty list (EDSM bug)
    if isinstance(sys_json["information"], (list,)):
        sys_json["information"] = {"factionState": None, "population": 0}

    # Then, get EDSM factions informations
    factions_infos = get_factions_from_edsm(system_name)

    # Then, get db system
    db_system = db.session.query(System).filter(System.name == system_name).first()

    # Then, get factions details and controlling faction name
    controlling_faction_name = "Unknown"
    if (
        factions_infos is not None
        and "controllingFaction" in factions_infos
        and factions_infos["controllingFaction"] is not None
    ):
        controlling_faction_name = factions_infos["controllingFaction"]["name"]

    # Build factions response
    factions_res = []
    if factions_infos is not None:
        for item in factions_infos["factions"]:
            factions_res.append(
                {
                    "name": item["name"],
                    "updated_at": arrow.Arrow.utcfromtimestamp(
                        item["lastUpdate"]
                    ).isoformat(),
                    "influence": item["influence"],
                    "state": get_faction_state_name(item["state"]),
                    "government": get_name_or_unknown(item["government"]),
                    "allegiance": get_name_or_unknown(item["allegiance"]),
                    "is_player": item["isPlayer"],
                    "happiness": item["happiness"],
                }
            )

    # Return result
    return {
        "name": sys_json["name"],
        "allegiance": get_name_or_unknown_from_obj("allegiance", db_system),
        "state": get_faction_state_name(sys_json["information"].get("factionState")),
        "government": get_name_or_unknown_from_obj("government", db_system),
        "security": get_name_or_unknown_from_obj("security", db_system),
        "primary_economy": get_name_or_unknown_from_obj("primary_economy", db_system),
        "controlling_faction_name": controlling_faction_name,
        "population": 0
        if "population" not in sys_json["information"]
        else sys_json["information"]["population"],
        "factions": factions_res,
        "permit_required": db_system.permit_required
        if db_system is not None
        else False,
        "updated_at": arrow.utcnow().isoformat(),
        "x": sys_json["coords"]["x"],
        "y": sys_json["coords"]["y"],
        "z": sys_json["coords"]["z"],
        "power": get_name_or_unknown_from_obj("power", db_system),
        "power_state": get_name_or_unknown_from_obj("power_state", db_system),
    }


def get_station_details(system_name, station_name):
    reference_system = (
        db.session.query(System).filter(System.name == system_name).first()
    )
    if reference_system is None:
        return error_response(system_name + " system not found")

    db_station = (
        db.session.query(Station)
        .filter(
            and_(Station.name == station_name, Station.system_id == reference_system.id)
        )
        .first()
    )
    if db_station is None:
        return error_response(station_name + " station not found")

    db_prices = (
        db.session.query(CommodityPrice)
        .filter(CommodityPrice.station_id == db_station.id)
        .all()
    )
    return {"station": db_station, "market": db_prices}


def get_stations_selling_buying_commodity(
    reference_system_name, commodity, min_stock, min_demand, pad_size, selling
):
    # First, try to get ref system from local db
    reference_system = (
        db.session.query(System).filter(System.name == reference_system_name).first()
    )
    # Else, try to get it from EDSM API
    if reference_system is None:
        reference_system = get_system_from_edsm(reference_system_name)
    if reference_system is None:
        return error_response(reference_system_name + " system not found")

    # Get commodity
    db_commodity = (
        db.session.query(Commodity)
        .filter(Commodity.name.ilike("%" + commodity + "%"))
        .first()
    )
    if db_commodity is None:
        return error_response("Commodity " + commodity + " not found")

    # Get nearby stations
    systems = (
        db.session.query(System)
        .filter(
            and_(
                System.x >= reference_system.x - 25,
                System.x <= reference_system.x + 25,
                System.y >= reference_system.y - 25,
                System.y <= reference_system.y + 25,
                System.z >= reference_system.z - 25,
                System.z <= reference_system.z + 25,
            )
        )
        .all()
    )

    # Build response
    res = []
    for system in systems:
        for station in system.stations:
            if can_dock_at_station(station.max_landing_pad, pad_size):
                if not selling:
                    price = (
                        db.session.query(CommodityPrice)
                        .filter(
                            and_(
                                CommodityPrice.commodity_id == db_commodity.id,
                                CommodityPrice.station_id == station.id,
                                CommodityPrice.buy_price != 0,
                            )
                        )
                        .first()
                    )
                else:
                    price = (
                        db.session.query(CommodityPrice)
                        .filter(
                            and_(
                                CommodityPrice.commodity_id == db_commodity.id,
                                CommodityPrice.station_id == station.id,
                                CommodityPrice.sell_price != 0,
                            )
                        )
                        .first()
                    )
                if price:
                    if (selling and price.demand >= min_demand) or (
                        (not selling) and price.supply >= min_stock
                    ):
                        res.append(
                            {
                                "station": station,
                                "supply": price.supply,
                                "demand": price.demand,
                                "buy_price": price.buy_price,
                                "sell_price": price.sell_price,
                                "distance": distance_between_systems(
                                    reference_system, station.system
                                ),
                                "last_price_update": arrow.Arrow.utcfromtimestamp(
                                    price.collected_at
                                ).isoformat(),
                                "distance_to_star": station.distance_to_star,
                                "price_difference_percentage": price_difference(
                                    db_commodity.average_price,
                                    price.buy_price
                                    if not selling
                                    else price.sell_price,
                                    selling,
                                ),
                            }
                        )

    res.sort(key=lambda obj: (obj["distance"], obj["distance_to_star"]))
    return res[:150]


def get_stations_selling_ship(reference_system_name, ship):
    # First, try to get ref system from local db
    reference_system = (
        db.session.query(System).filter(System.name == reference_system_name).first()
    )
    # Else, try to get it from EDSM API
    if reference_system is None:
        reference_system = get_system_from_edsm(reference_system_name)
    if reference_system is None:
        return error_response(reference_system_name + " system not found")

    ship_id = db.session.query(Ship).filter(Ship.name.ilike("%" + ship + "%")).first()
    if ship_id is None:
        return error_response("Ship " + ship + " not found")
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
    return ret_list[:150]
