import json

import arrow
import requests
from flask import Blueprint, jsonify

from api.helpers.request import get_requests_headers
from api.helpers.response import error_response
from api.extensions.cache import cache

news_bp = Blueprint("news", __name__)


@news_bp.route("/")
@cache.cached(timeout=900)
def flask_get_news():
    # Get articles
    url = "https://cms.zaonce.net/en-GB/jsonapi/node/news_article"
    url += "?include=field_image_entity.field_media_image,field_site"
    url += "&filter[site][condition][path]=field_site.field_slug"
    url += "&filter[site][condition][operator]=CONTAINS"
    url += "&filter[site][condition][value]=elite-dangerous&sort[sort-published][path]=published_at"
    url += "&sort[sort-published][direction]=DESC&page[offset]=0&page[limit]=6"

    req = requests.get(url, headers=get_requests_headers())
    if req.status_code != 200:
        return error_response("Cannot fetch content", 500)
    articles = json.loads(req.content.decode("utf-8"))["data"]

    # Build response
    res = []
    for item in articles:
        new_item = {
            "uri": f"https://www.elitedangerous.com/news/{item['attributes']['field_slug']}",
            "content": item['attributes']["body"]['value'],
            "title": item['attributes']["title"],
            "id": int(item["attributes"]["drupal_internal__nid"]),
            "timestamp": arrow.get(item['attributes']["published_at"]).timestamp,
            "picture": None,
        }

        res.append(new_item)
    return jsonify(res)
