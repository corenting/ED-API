import json

import arrow
import requests
from flask import Blueprint, request, jsonify
from requests.exceptions import RequestException

from api.helpers.request import get_requests_headers
from api.helpers.response import error_response

galnet_bp = Blueprint("galnet", __name__)


@galnet_bp.route("/")
def flask_get_galnet():
    # Get articles
    lang = request.args.get("lang")
    if lang is None or lang == "en":
        url = "https://rss-bridge.9cw.eu/?action=display&bridge=EliteDangerousGalnet&format=Json"
    else:
        url = (
            "https://rss-bridge.9cw.eu/?action=display&bridge=EliteDangerousGalnet&format=Json&language="
            + lang
        )
    req = requests.get(url, headers=get_requests_headers(), timeout=1)
    if req.status_code != 200:
        return error_response("Cannot fetch content", 500)
    articles = json.loads(req.content.decode("utf-8"))

    # Get official website JSON for the pictures
    try:
        website_api_req = requests.get(
            "https://elitedangerous-website-backend-production.elitedangerous.com/api/galnet?_format=json",
            headers=get_requests_headers(),
            timeout=1,
        )
        if website_api_req.status_code == 200:
            # only first 15 elements like other source used
            website_api_content = json.loads(website_api_req.content.decode("utf-8"))[:15]
    except RequestException:
        website_api_content = []

    # Build response
    res = []
    for item in articles["items"]:
        new_item = {
            "uri": item["url"],
            "content": item["content_html"]
            if "content_html" in item
            else "No description",
            "title": item["title"],
            "timestamp": arrow.get(item["date_modified"]).timestamp,
        }

        # Add picture URL from website if available
        website_item = next(
            (x for x in website_api_content if x["title"] == item["title"]), None
        )
        if website_item is not None:
            base_url = "http://hosting.zaonce.net/elite-dangerous/galnet/"
            picture_name = website_item["image"]
            if "," in picture_name:
                picture_name = picture_name.split(",")[0]

            new_item["picture"] = f"{base_url}{picture_name}.png"

        res.append(new_item)
    return jsonify(res)
