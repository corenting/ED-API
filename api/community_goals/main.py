import json

import arrow
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

from api.helpers.request import get_requests_headers
from api.helpers.response import error_response
from config import APP_VERSION, DEBUG_MODE, INARA_API_KEY

community_goals_bp = Blueprint("community_goals", __name__)


@community_goals_bp.route("/v2/")
def flask_old_get_redirect():
    return flask_get_community_goals()


@community_goals_bp.route("/")
def flask_get_community_goals():
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
        return error_response("Cannot contact Inara API", status_code=500)

    inara_api_response = json.loads(req.content.decode("utf-8"))

    try:
        if (
            inara_api_response["header"]["eventStatus"] != 200
            and inara_api_response["events"][0]["eventStatus"] != 200
        ):
            return error_response("Inara returned an error", status_code=500)
    except:
        return error_response(
            "Unknown error while processing Inara API response", status_code=500
        )

    # Get page for rewards
    rewards_ok = False
    rewards = []
    try:
        req_page = requests.get(
            "https://inara.cz/galaxy-communitygoals", headers=get_requests_headers()
        )
        if req_page.status_code == 200:
            rewards_ok = True
            soup = BeautifulSoup(req_page.content, "html5lib")
            rewards = soup.select("table")
    except:
        pass

    # Prepare response
    response = []

    #  If no ongoing goals return earlier
    if "eventData" not in inara_api_response["events"][0]:
        return jsonify(response)

    idx = 0
    for event in inara_api_response["events"][0]["eventData"]:
        rewards_result = []
        try:
            # Get corresponding rewards array
            if rewards_ok:
                rewards_table = rewards[idx].select("tr")[
                    1:
                ]  # remove first line (table headers)
                for reward_line in rewards_table:
                    new_result = {
                        "tier": reward_line.select("td")[0].text,
                        "contributors": reward_line.select("td")[1].text,
                        "reward": reward_line.select("td")[2].text,
                    }
                    rewards_result.append(new_result)
        except:
            pass

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
            "rewards": rewards_result,
        }

        idx = idx + 1

        response.append(goal)

    return jsonify(response)
