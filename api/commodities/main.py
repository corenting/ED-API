import arrow
from flask import Blueprint, request
from sqlalchemy import text, desc, asc, and_

from api.database import db
from api.helpers.response import get_response, error_response
from common.market import price_difference
from models.database import Commodity, CommodityPrice, Station

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
        'select '
        'avg(buy_price) as buy_avg,'
        'avg(sell_price) as sell_avg,'
        'min(nullif(buy_price, 0)) as min_buy,'
        'max(sell_price) as max_sell '
        'from commodities_prices '
        'where commodity_id = :id group by commodity_id;'),
        id=db_commodity.id).fetchall()

    # Get maximum selling stations and minimum buying ones
    max_sellers = db.session.query(CommodityPrice).join(
        CommodityPrice.station
    ).filter(
        CommodityPrice.commodity_id == db_commodity.id
    ).order_by(desc(CommodityPrice.sell_price)).limit(25).all()

    min_buyers = db.session.query(CommodityPrice).join(
        CommodityPrice.station
    ).filter(and_(
        CommodityPrice.commodity_id == db_commodity.id,
        CommodityPrice.buy_price != 0
    )).order_by(asc(CommodityPrice.buy_price)).limit(25).all()

    item = {
        'average_price': db_commodity.average_price,
        'category': db_commodity.category,
        'id': db_commodity.id,
        'is_rare': db_commodity.is_rare,
        'name': db_commodity.name,
        'average_buy_price': float(live_avg[0][0]) if live_avg is not None else None,
        'average_sell_price': float(live_avg[0][1]) if live_avg is not None else None,
        'minimum_buy_price': float(live_avg[0][2]) if live_avg is not None else None,
        'maximum_sell_price': float(live_avg[0][3]) if live_avg is not None else None,
        'maximum_sellers': [{
            'station': x.station,
            'supply': x.supply,
            'sell_price': x.sell_price,
            'demand': x.demand,
            'collected_at': arrow.get(x.collected_at).isoformat(),
            'price_difference_percentage':
                price_difference(db_commodity.average_price, x.sell_price, is_selling=True)
        } for x in max_sellers],
        "minimum_buyers": [{
            'station': x.station,
            'supply': x.supply,
            'buy_price': x.buy_price,
            'demand': x.demand,
            'collected_at': arrow.get(x.collected_at).isoformat(),
            'price_difference_percentage':
                price_difference(db_commodity.average_price, x.buy_price, is_selling=False)
        } for x in min_buyers]
    }

    # Add max profit
    max_profit = None
    if live_avg is not None:
        max_profit = item['maximum_sell_price'] - item['minimum_buy_price']
    item['maximum_profit'] = max_profit

    return item


def get_commodities_list(name_filter, live_price=False):
    if not name_filter:
        db_list = db.session.query(Commodity).all()
    else:
        db_list = db.session.query(Commodity).filter(Commodity.name.ilike('%' + name_filter + '%')).all()

    if live_price and not name_filter:
        new_results = []
        live_results = db.engine.execute(
            'select commodity_id, avg(buy_price) as buy_avg, avg(sell_price) as sell_avg '
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
