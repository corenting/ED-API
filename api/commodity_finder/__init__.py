from flask import Blueprint, redirect, jsonify

from api.extensions.database import db
from api.helpers.response import error_response
from common.edsm import get_system
from common.space import distance_between_systems
from models.database import Commodity, CommodityPrice, Ship, StationShipLink, System
from requests.api import request
from api.helpers.request import request_param
from sqlalchemy import and_
from common.station import can_dock_at_station
import arrow
from common.market import price_difference

ship_finder_bp = Blueprint("ship_finder", __name__)


@ship_finder_bp.route("/")
def flask_find_commodity():
    # Get params
    system_name = request.args.get("referenceSystem")
    commodity_name = request.args.get("commodityName")
    pad_size = request_param("pad", "S")
    min_stock = request_param("stock", 1)
    selling = request_param("selling", False) == "true"
    min_demand = request_param("demand", 0)

    # First, try to get ref system from local db
    reference_system = (
        db.session.query(System).filter(System.name == system_name).first()
    )
    # Else, try to get it from EDSM API
    if reference_system is None:
        reference_system = get_system(system_name)
    if reference_system is None:
        return error_response(f"{system_name} system not found")

    # Get commodity
    db_commodity = (
        db.session.query(Commodity)
        .filter(Commodity.name.ilike(f"%{commodity_name}"))
        .first()
    )
    if db_commodity is None:
        return error_response(f"Commodity {commodity_name} not found")

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
    return jsonify(res[:150])
