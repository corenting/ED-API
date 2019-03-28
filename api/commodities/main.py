from flask import Blueprint, request
from sqlalchemy import text

from api.database import db
from api.helpers.response import get_response, error_response
from models.database import Commodity

commodities_bp = Blueprint("commodities", __name__)


@commodities_bp.route("/")
def flask_get_commodities():
    return get_response(get_commodities_list(request.args.get('name'), request.args.get('live_prices')))


@commodities_bp.route("/<name>")
def flask_get_commodity(name):
    return get_response(get_commodity(name))


def get_commodity(name_filter):
    db_commodity = db.session.query(Commodity).filter(Commodity.name.ilike('%' + name_filter + '%')).first()
    if db_commodity is None:
        return error_response('Commodity not found')

    # Get average sell/buy prices
    live_avg = db.engine.execute(text(
        'select commodity_id, avg(buy_price) as buy_avg,'
        'avg(sell_price) as sell_avg from commodities_prices '
        'where commodity_id = :id group by commodity_id;'),
        id=db_commodity.id).fetchall()

    return {
        'average_price': db_commodity.average_price,
        'category': db_commodity.category,
        'id': db_commodity.id,
        'is_rare': db_commodity.is_rare,
        'name': db_commodity.name,
        'average_buy_price': float(live_avg[0][1]) if live_avg is not None else None,
        'average_sell_price': float(live_avg[0][2]) if live_avg is not None else None
    }


def get_commodities_list(name_filter, live_price=False):
    if not name_filter:
        db_list = db.session.query(Commodity).all()
    else:
        db_list = db.session.query(Commodity).filter(Commodity.name.ilike('%' + name_filter + '%')).all()

    if live_price and not name_filter:
        new_results = []
        live_results = db.engine.execute(
            'select commodity_id, avg(buy_price) as buy_avg, avg(sell_price) as sell_avg'
            'from commodities_prices group by commodity_id;').fetchall()
        for entry in db_list:
            live_entry = next((x for x in live_results if x[0] == entry.id), None)
            new_results.append({
                'average_price': entry.average_price,
                'category': entry.category,
                'id': entry.id,
                'is_rare': entry.is_rare,
                'name': entry.name,
                'average_buy_price': float(live_entry[1]) if live_entry is not None else None,
                'average_sell_price': float(live_entry[2]) if live_entry is not None else None,
            })
        return new_results
    else:
        return db_list
