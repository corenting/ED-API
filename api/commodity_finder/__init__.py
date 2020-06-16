import arrow
from flask import Blueprint, jsonify, request
from sqlalchemy import and_, text

from api.extensions.database import db
from api.helpers.request import request_param
from api.helpers.response import error_response
from common.edsm import get_system
from common.market import price_difference
from common.space import distance_between_systems
from common.station import can_dock_at_station
from models.database import Commodity, CommodityPrice, System

commodity_finder_bp = Blueprint("commodity_finder", __name__)


@commodity_finder_bp.route("/")
def flask_find_commodity():
    """Find a station to buy or sell a specific commodity
    ---
    tags:
      - Commodity finder
    definitions:
      CommodityFinderError:
        type: object
        properties:
          error:
            type: string
    parameters:
      - name: referenceSystem
        in: query
        type: string
        required: true
        description: Reference system to search around
      - name: commodityName
        in: query
        type: string
        required: true
        description: The commodity to search
      - name: pad
        in: query
        type: string
        required: false
        default: S
        enum: [S, M, L]
        description: Minimum required landing pad size
      - name: stock
        in: query
        type: integer
        required: false
        default: 1
        description: Minimum stock (if buying)
      - name: selling
        in: query
        type: boolean
        required: false
        description: If true, search for a station selling a commodity, else for a station buying it
      - name: demand
        in: query
        type: integer
        required: false
        default: 0
        description: Minimum stock (if buying)
    responses:
      200:
        description: A list of stations buying/selling this commodity
      500:
        description: Error while searching
        schema:
          $ref: '#/definitions/CommodityFinderError'
    """
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

    # Get prices
    db_ids = db.engine.execute(
        text(
            "select cp.id from commodities_prices cp "
            "join stations st on st.id = cp.station_id "
            "join systems s on s.id = st.system_id "
            "where commodity_id = :commodity_id "
            "and s.x >= :ref_system_x - 25 "
            "and s.x <= :ref_system_x + 25 "
            "and s.y >= :ref_system_y - 25 "
            "and s.y <= :ref_system_y + 25 "
            "and s.z >= :ref_system_z - 25 "
            "and s.z <= :ref_system_z + 25 "
            f"and {'sell_price' if selling else 'buy_price'} != 0;"
        ),
        commodity_id=db_commodity.id,
        ref_system_x=reference_system.x,
        ref_system_y=reference_system.y,
        ref_system_z=reference_system.z,
    ).fetchall()
    ids_to_fetch = (i[0] for i in db_ids)

    prices = db.session.query(CommodityPrice).join(CommodityPrice.station).filter(CommodityPrice.id.in_(ids_to_fetch)).all()

    res = []
    for item in prices:
        if (selling and item.demand >= min_demand) or (
                (not selling) and item.supply >= min_stock
        ):
            res.append(
                {
                    "station": item.station,
                    "supply": item.supply,
                    "demand": item.demand,
                    "buy_price": item.buy_price,
                    "sell_price": item.sell_price,
                    "distance": distance_between_systems(
                        reference_system, item.station.system
                    ),
                    "last_price_update": arrow.Arrow.utcfromtimestamp(
                        item.collected_at
                    ).isoformat(),
                    "distance_to_star": item.station.distance_to_star,
                    "price_difference_percentage": price_difference(
                        db_commodity.average_price,
                        item.buy_price
                        if not selling
                        else item.sell_price,
                        selling,
                    ),
                }
            )

    res.sort(key=lambda obj: (obj["distance"], obj["distance_to_star"]))
    return jsonify(res[:150])
