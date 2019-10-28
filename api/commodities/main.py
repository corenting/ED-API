import arrow
from flask import Blueprint, request, jsonify
from sqlalchemy import text, desc, asc, and_

from api.database import db
from api.helpers.response import error_response
from common.market import price_difference
from models.database import Commodity, CommodityPrice

commodities_bp = Blueprint("commodities", __name__)


@commodities_bp.route("/")
def flask_get_commodities():
    name_filter = request.args.get("name")
    live_price = request.args.get("live_prices") == 1

    # Get all commodities or only the ones corresponding to the filter
    if not name_filter:
        db_list = db.session.query(Commodity).all()
    else:
        db_list = (
            db.session.query(Commodity)
            .filter(Commodity.name.ilike("%" + name_filter + "%"))
            .all()
        )

    if live_price and not name_filter:
        new_results = []
        average_prices = db.engine.execute(
            "select commodity_id, avg(buy_price) as buy_avg, avg(sell_price) as sell_avg "
            "from commodities_prices group by commodity_id;"
        ).fetchall()
        for entry in db_list:
            commodity_avg_prices = next(
                (x for x in average_prices if x[0] == entry.id), None
            )
            new_results.append(
                {
                    "average_price": entry.average_price,
                    "category": entry.category,
                    "id": entry.id,
                    "is_rare": entry.is_rare,
                    "name": entry.name,
                    "average_buy_price": float(commodity_avg_prices[1])
                    if commodity_avg_prices is not None
                    else None,
                    "average_sell_price": float(commodity_avg_prices[2])
                    if commodity_avg_prices is not None
                    else None,
                }
            )
        return jsonify(new_results)
    else:
        return jsonify(db_list)


@commodities_bp.route("/<name>")
def flask_get_commodity(name):
    # Fetch the commodity from the db by name
    db_commodity = (
        db.session.query(Commodity)
        .filter(Commodity.name.ilike("%" + name + "%"))
        .first()
    )
    if db_commodity is None:
        return error_response("Commodity not found")

    # Get average sell/buy prices
    live_avg = db.engine.execute(
        text(
            "select "
            "avg(buy_price) as buy_avg,"
            "avg(sell_price) as sell_avg,"
            "min(nullif(buy_price, 0)) as min_buy,"
            "max(sell_price) as max_sell "
            "from commodities_prices "
            "where commodity_id = :id group by commodity_id;"
        ),
        id=db_commodity.id,
    ).fetchall()[0]

    # Get maximum selling stations
    max_sellers = (
        db.session.query(CommodityPrice)
        .join(CommodityPrice.station)
        .filter(CommodityPrice.commodity_id == db_commodity.id)
        .order_by(desc(CommodityPrice.sell_price))
        .limit(25)
        .all()
    )

    # Get min buying stations
    min_buyers = (
        db.session.query(CommodityPrice)
        .join(CommodityPrice.station)
        .filter(
            and_(
                CommodityPrice.commodity_id == db_commodity.id,
                CommodityPrice.buy_price != 0,
            )
        )
        .order_by(asc(CommodityPrice.buy_price))
        .limit(25)
        .all()
    )

    # Prices
    if live_avg is None:
        prices = {
            "average_buy_price": 0,
            "average_sell_price": 0,
            "minimum_buy_price": 0,
            "maximum_sell_price": 0,
        }
    else:
        prices = {
            "average_buy_price": float(live_avg[0]) if live_avg[0] is not None else 0,
            "average_sell_price": float(live_avg[1]) if live_avg[1] is not None else 0,
            "minimum_buy_price": float(live_avg[2]) if live_avg[2] is not None else 0,
            "maximum_sell_price": float(live_avg[3]) if live_avg[3] is not None else 0,
        }

    item = {
        **prices,
        "average_price": db_commodity.average_price,
        "category": db_commodity.category,
        "id": db_commodity.id,
        "is_rare": db_commodity.is_rare,
        "name": db_commodity.name,
        "maximum_sellers": [
            {
                "station": x.station,
                "supply": x.supply,
                "sell_price": x.sell_price,
                "demand": x.demand,
                "collected_at": arrow.get(x.collected_at).isoformat(),
                "price_difference_percentage": price_difference(
                    db_commodity.average_price, x.sell_price, is_selling=True
                ),
            }
            for x in max_sellers
        ],
        "minimum_buyers": [
            {
                "station": x.station,
                "supply": x.supply,
                "buy_price": x.buy_price,
                "demand": x.demand,
                "collected_at": arrow.get(x.collected_at).isoformat(),
                "price_difference_percentage": price_difference(
                    db_commodity.average_price, x.buy_price, is_selling=False
                ),
            }
            for x in min_buyers
        ],
    }

    # Add max profit
    max_profit = None
    if live_avg is not None:
        max_profit = max(item["maximum_sell_price"] - item["minimum_buy_price"], 0)
    item["maximum_profit"] = max_profit

    return jsonify(item)
