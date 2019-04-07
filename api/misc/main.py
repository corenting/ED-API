import json

import arrow
import requests
from flask import Blueprint, request, redirect

from api.database import db
from api.helpers.request import get_requests_headers
from api.helpers.response import error_response, get_response
from common.edsm import get_system_from_edsm
from common.space import distance_between_systems
from models.database import System, Ship

misc_bp = Blueprint("misc", __name__)


@misc_bp.route("/")
def flask_hello():
    return "ED-API is running."


@misc_bp.route("/ships/")
def flask_get_ships():
    return get_response(get_ships_list(request.args.get('name')))


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


@misc_bp.route("/galnet/")
def flask_get_galnet():
    lang = request.args.get('lang')
    if lang is None or lang == 'en':
        url = "https://9cw.eu/rss-bridge/?action=display&bridge=EliteDangerousGalnet&format=Json"
    else:
        url = "https://9cw.eu/rss-bridge/?action=display&bridge=EliteDangerousGalnet&format=Json&language=" + lang

    req = requests.get(url, headers=get_requests_headers())
    if req.status_code != 200:
        return error_response('Cannot fetch content')

    content = json.loads(req.content.decode("utf-8"))
    res = []
    for item in content['items']:
        res.append({
            'uri': item['url'],
            'content': item['content_html'],
            'title': item['title'],
            'timestamp': arrow.get(item['date_modified']).timestamp,

        })
    return get_response(res)


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


def get_ships_list(name_filter):
    if not name_filter:
        db_list = db.session.query(Ship).all()
    else:
        db_list = db.session.query(Ship).filter(Ship.name.ilike('%' + name_filter + '%')).all()
    return db_list
