import json

import arrow
import requests
from flask import Blueprint, request, jsonify

from api.helpers.request import get_requests_headers
from api.helpers.response import error_response

news_bp = Blueprint("news", __name__)


@news_bp.route("/")
def flask_get_news():
    # Get articles
    url = "https://elitedangerous-website-backend-production.elitedangerous.com/api/news?_format=json"
    req = requests.get(url, headers=get_requests_headers())
    if req.status_code != 200:
        return error_response("Cannot fetch content", 500)
    articles = json.loads(req.content.decode("utf-8"))

    # Build response
    res = []
    for item in articles:
        new_item = {
            "uri": item["forumLink"],
            "content": item["body"],
            "title": item["title"],
            "id": int(item["nid"]),
            "timestamp": arrow.get(item["date"]).timestamp,
            "picture": "https://cms.elitedangerous.com/frontier_image_styles/style?url={}&width=1280&height=720&type=binary".format(
                item["image"]
            ),
        }

        res.append(new_item)
    return jsonify(res)
