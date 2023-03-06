from typing import Optional

import pendulum
from cachier import cachier

from app import __version__
from app.config import DEBUG, INARA_API_KEY
from app.database.community_goal_status import CommunityGoalStatus
from app.database.database import Session
from app.helpers.fcm import send_fcm_notification
from app.helpers.httpx import get_httpx_client
from app.models.community_goals import CommunityGoal
from app.models.exceptions import ContentFetchingException
from loguru import logger


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
    def get_community_goals(self) -> list[CommunityGoal]:
        """Get latest community goals informations."""
        inara_res = _get_community_goals_from_inara()
        if (
            inara_res.get("header", {}).get("eventStatus", None) != 200
            and inara_res.get("events", [{}])[0].get("eventStatus") != 200
        ):
            raise ContentFetchingException()

        # Return empty if no CGs running
        if "eventData" not in inara_res["events"][0]:
            return []

        return [
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
        ]

    def _send_notification_for_change(
        self, change_type: str, goal: CommunityGoalStatus
    ) -> None:
        notification = {
            "title": goal.title,
            "current_tier": str(goal.current_tier),
            "date": pendulum.now().to_iso8601_string(),
        }

        if send_fcm_notification(change_type, goal.title, notification):
            logger.info("FCM notification sent")
        else:
            logger.error("Failed to send FCM message")

    def _compare_data(
        self, previous: list[CommunityGoalStatus], latest: list[CommunityGoalStatus]
    ) -> None:
        for goal in latest:
            logger.info(f"Checking for updates for {goal.title}...")
            previous_goal = next((x for x in previous if x.id == goal.id), None)

            # New goal
            if previous_goal is None:
                logger.info(
                    f"Goal {goal.title} started", extra={"community_goal": goal}
                )
                self._send_notification_for_change("new_goal", goal)
                continue

            # Finished goal
            if goal.is_finished and not previous_goal.is_finished:
                logger.info(
                    f"Goal {goal.title} finished", extra={"community_goal": goal}
                )
                self._send_notification_for_change("finished_goal", goal)
                continue

            # Check if new tier
            if goal.current_tier > previous_goal.current_tier and not goal.is_finished:
                logger.info(
                    f"Goal {goal.title} changed tier ({goal.current_tier} from {previous_goal.current_tier})",
                    extra={"community_goal": goal},
                )
                self._send_notification_for_change("new_tier", goal)
                continue

            logger.info(f"No updates for {goal.title}")

    def _store_updated_data(
        self,
        latest_data: list[CommunityGoalStatus],
        previous_data: Optional[list[CommunityGoalStatus]],
    ) -> None:
        with Session.begin() as session:
            # If no previous data, store all
            if previous_data is None:
                for item in latest_data:
                    session.add(item)
                return

            # Else compare to not store bad data
            for item in latest_data:
                previous_item = next(
                    (x for x in previous_data if x.id == item.id), None
                )

                # No previous item, store
                if previous_item is None:
                    session.add(item)
                    continue

                # If previous has bigger tier, don't save new one
                if previous_item.current_tier > item.current_tier:
                    continue

                # If previous is finished but now is ongoing, ignore
                if previous_item.is_finished and not item.is_finished:
                    continue

                # Else, update
                db_item = (
                    session.query(CommunityGoalStatus)
                    .filter(CommunityGoalStatus.id == item.id)
                    .one()
                )
                db_item.id = item.id
                db_item.last_update = item.last_update
                db_item.is_finished = item.is_finished
                db_item.current_tier = item.current_tier
                db_item.title = item.title

    def send_notifications(self) -> None:
        """Send a FCM notification with CGs changes."""
        logger.info("Checking for CGs changes...")

        # First get latest data
        goals: list[CommunityGoal] = self.get_community_goals()
        data_to_save = [
            CommunityGoalStatus(
                id=goal.id,
                last_update=goal.last_update,
                is_finished=not goal.ongoing,
                current_tier=goal.current_tier,
                title=goal.title,
            )
            for goal in goals
            if goal.title
        ]

        # Get previous data from db
        with Session.begin() as session:
            previous_data = session.query(CommunityGoalStatus).all()

            # If no previous data, write it and exit
            if len(previous_data) == 0:
                self._store_updated_data(data_to_save, None)
                return

            # Else compare
            self._compare_data(previous_data, data_to_save)

            # Then replace previous
            self._store_updated_data(data_to_save, previous_data)
