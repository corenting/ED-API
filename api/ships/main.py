import json

import requests
from flask import Blueprint, request, redirect

from api.database import db
from api.helpers.request import get_requests_headers
from api.helpers.response import get_response, error_response
from models.database import Ship

ships_bp = Blueprint("ships", __name__)


@ships_bp.route("/")
def flask_get_ships():
    return get_response(get_ships_list(request.args.get('name')))


@ships_bp.route("/details")
def flask_get_ships_details():
    res = get_ships_details(request.args.get('name'))
    if res is None:
        res = error_response('Ship not found')
    return get_response(res)


@ships_bp.route("/picture/<ship>")
def flask_get_ship_picture(ship):
    res_item = get_ships_details(ship)
    if res_item is None:
        return get_response(error_response('Ship not found'))
    else:
        return redirect(res_item['landing_pad_picture'], 301)


def get_ships_details(filter_ship_name):
    url_base = 'https://elitedangerous-website-backend-production.elitedangerous.com'
    url = "{0}/api/ships?_format=json".format(url_base)
    req = requests.get(url, headers=get_requests_headers())
    if req.status_code != 200:
        return error_response('Cannot fetch content')

    content = json.loads(req.content.decode("utf-8"))
    res = []
    for item in content:
        ship_name = get_ship_name(item['slug'])
        if ship_name is None:
            continue
        res.append({
            'name': ship_name,
            'landing_pad_picture': '{0}{1}'.format(url_base, item['threeQuarterImage']),
            'description': item['body'].replace('<p>', '').replace('</p>', ''),

        })

    # Send response
    if filter_ship_name is None:
        return res
    else:
        res = next((x for x in res if x['name'].lower() == filter_ship_name.lower()), None)
        return res


def get_ship_name(name):
    internal_names = {
        'adder': 'Adder',
        'alliance-challenger': 'Alliance Challenger',
        'alliance-chieftain': 'Alliance Chieftain',
        'alliance-crusader': 'Alliance Crusader',
        'anaconda': 'Anaconda',
        'asp-explorer': 'Asp Explorer',
        'asp-scout': 'Asp Scout',
        'beluga-liner': 'Beluga Liner',
        'cobra-mk-iii': 'Cobra MkIII',
        'cobra-mk-iv': 'Cobra MkIV',
        'diamondback-explorer': 'Diamondback Explorer',
        'diamondback-scout': 'Diamondback Scout',
        'dolphin': 'Dolphin',
        'eagle': 'Eagle',
        'federal-assault-ship': 'Federal Assault Ship',
        'federal-corvette': 'Federal Corvette',
        'federal-dropship': 'Federal Dropship',
        'federal-gunship': 'Federal Gunship',
        'fer-de-lance': 'Fer-de-Lance',
        'hauler': 'Hauler',
        'imperial-clipper': 'Imperial Clipper',
        'imperial-courier': 'Imperial Courier',
        'imperial-cutter': 'Imperial Cutter',
        'imperial-eagle': 'Imperial Eagle',
        'keelback': 'Keelback',
        'krait-mk-ii': 'Krait MkII',
        'krait-phantom': 'Krait Phantom',
        'mamba': 'Mamba',
        'orca': 'Orca',
        'python': 'Python',
        'sidewinder': 'Sidewinder',
        'type-6': 'Type-6 Transporter',
        'type-7': 'Type-7 Transporter',
        'type-9': 'Type-9 Heavy',
        'type-10': 'Type-10 Defender',
        'viper-mk-iii': 'Viper MkIII',
        'viper-mk-iv': 'Viper MkIV',
        'vulture': 'Vulture',
    }

    if name in internal_names:
        return internal_names[name]
    return None


def get_ships_list(name_filter):
    if not name_filter:
        db_list = db.session.query(Ship).all()
    else:
        db_list = db.session.query(Ship).filter(Ship.name.ilike('%' + name_filter + '%')).all()
    return db_list
