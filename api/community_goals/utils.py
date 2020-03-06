import json

import arrow
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

from api.helpers.request import get_requests_headers
from config import APP_VERSION, DEBUG_MODE, INARA_API_KEY
from api.helpers.response import error_response


def get_community_goals():
    request_body = {
        "header": {
            "appName": "EDCompanion",
            "appVersion": APP_VERSION,
            "isDeveloped": DEBUG_MODE,
            "APIkey": INARA_API_KEY,
        },
        "events": [
            {
                "eventName": "getCommunityGoalsRecent",
                "eventTimestamp": arrow.utcnow().isoformat(),
                "eventData": [],
            }
        ],
    }

    # Get API
    req = requests.post(
        "https://inara.cz/inapi/v1/", headers=get_requests_headers(), json=request_body
    )
    # Check for errors
    if req.status_code != 200:
        return error_response("Cannot fetch content from Inara", 500)

    inara_api_response = json.loads(req.content.decode("utf-8"))

    try:
        if (
            inara_api_response["header"]["eventStatus"] != 200
            and inara_api_response["events"][0]["eventStatus"] != 200
        ):
            return error_response("Error parsing content from Inara", 500)
    except:
        return error_response("Error parsing content from Inara", 500)

    # Prepare response
    api_response = []

    # Check if there is any ongoing community goals
    if "eventData" not in inara_api_response["events"][0]:
        return jsonify(api_response)

    idx = 0
    for event in inara_api_response["events"][0]["eventData"]:
        rewards_result = []

        # Build goal response
        goal = {
            "title": event["communitygoalName"],
            "id": event["communitygoalGameID"],
            "date": {"end": event["goalExpiry"], "last_update": event["lastUpdate"]},
            "location": {
                "station": event["stationName"],
                "system": event["starsystemName"],
            },
            "tier_progress": {
                "current": event["tierReached"],
                "total": event["tierMax"],
            },
            "objective": event["goalObjectiveText"],
            "reward": event["goalRewardText"],
            "contributors": event["contributorsNum"],
            "ongoing": not event["isCompleted"],
            "description": event["goalDescriptionText"],
        }

        idx = idx + 1

        api_response.append(goal)

    return jsonify(api_response)
