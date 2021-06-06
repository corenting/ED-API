from typing import Generator

import pendulum
from cachier import cachier

from app import __version__
from app.config import DEBUG, INARA_API_KEY
from app.helpers.httpx import get_httpx_client
from app.models.community_goals import CommunityGoal
from app.models.exceptions import ContentFetchingException


@cachier(stale_after=pendulum.duration(minutes=10))
def _get_community_goals_from_inara() -> dict:
    request_body = {
        "header": {
            "appName": "EDCompanion",
            "appVersion": __version__,
            "isDeveloped": DEBUG,
            "APIkey": INARA_API_KEY,
        },
        "events": [
            {
                "eventName": "getCommunityGoalsRecent",
                "eventTimestamp": pendulum.now("UTC").to_iso8601_string(),
                "eventData": [],
            }
        ],
    }

    # Get API
    with get_httpx_client() as client:
        res = client.post("https://inara.cz/inapi/v1/", json=request_body)

    return res.json()


class CommunityGoalsService:
    def get_community_goals(self) -> Generator[CommunityGoal, None, None]:
        """Get latest community goals informations."""
        inara_res = _get_community_goals_from_inara()
        if (
            inara_res.get("header", {}).get("eventStatus", None) != 200
            and inara_res.get("events", [{}])[0].get("eventStatus") != 200
        ):
            raise ContentFetchingException()

        # Return empty if no CGs running
        if "eventData" not in inara_res["events"][0]:
            return (_ for _ in ())

        return (
            CommunityGoal(
                contributors=event["contributorsNum"],
                current_tier=event["tierReached"],
                description=event["goalDescriptionText"],
                end_date=pendulum.parse(event["goalExpiry"]),  # type: ignore
                last_update=pendulum.parse(event["lastUpdate"]),  # type: ignore
                objective=event["goalObjectiveText"],
                ongoing=not event["isCompleted"],
                reward=event["goalRewardText"],
                station=event["stationName"],
                system=event["starsystemName"],
                max_tier=event["tierMax"],
                title=event["communitygoalName"],
                id=event["communitygoalGameID"],
            )
            for event in inara_res["events"][0]["eventData"]
        )
