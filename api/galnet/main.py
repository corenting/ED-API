import json

import arrow
import requests
from flask import Blueprint, request

from api.helpers.request import get_requests_headers
from api.helpers.response import error_response, get_response

galnet_bp = Blueprint("galnet", __name__)


@galnet_bp.route("/")
def flask_get_galnet():
    # Get articles
    lang = request.args.get('lang')
    if lang is None or lang == 'en':
        url = "https://9cw.eu/rss-bridge/?action=display&bridge=EliteDangerousGalnet&format=Json"
    else:
        url = "https://9cw.eu/rss-bridge/?action=display&bridge=EliteDangerousGalnet&format=Json&language=" + lang
    req = requests.get(url, headers=get_requests_headers())
    if req.status_code != 200:
        return error_response('Cannot fetch content')
    articles = json.loads(req.content.decode("utf-8"))

    # Get official website JSON for the pictures
    website_api_content = []
    website_api_req = requests.get(
        'https://elitedangerous-website-backend-production.elitedangerous.com/api/galnet?_format=json',
        headers=get_requests_headers())
    if website_api_req.status_code == 200:
        # only first 15 elements like other source used
        website_api_content = json.loads(website_api_req.content.decode("utf-8"))[:15]

    # Build response
    res = []
    for item in articles['items']:
        new_item = {
            'uri': item['url'],
            'content': item['content_html'] if 'content_html' in item else 'No description',
            'title': item['title'],
            'timestamp': arrow.get(item['date_modified']).timestamp,
        }

        # Add picture URL from website if available
        website_item = next((x for x in website_api_content if x['title'] == item['title']), None)
        if website_item is not None:
            new_item['picture'] = 'http://hosting.zaonce.net/elite-dangerous/galnet/{}.png'.format(
                website_item['image'])

        res.append(new_item)
    return get_response(res)
