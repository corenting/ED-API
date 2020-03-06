import logging
from datetime import datetime

import arrow
from pyfcm import FCMNotification
from sqlalchemy import create_engine

from api.community_goals import get_community_goals
from config import DB_URI, DEBUG_MODE, FCM_API_KEY
from models.database import CommunityGoalStatus, get_session

logger = logging.getLogger(__name__)
push_service = FCMNotification(api_key=FCM_API_KEY)
db_engine = create_engine(DB_URI)


def send_fcm_notification(topic, data):
    if DEBUG_MODE:
        topic += "_test"
    extra_kwargs = {"priority": "high"}

    return push_service.notify_topic_subscribers(
        topic_name=topic,
        data_message=data,
        extra_kwargs=extra_kwargs,
        collapse_key=data["goal"]["title"],
        time_to_live=86400,
    )


def handle_change(change_type, goal):
    notif_goal = {"title": goal.title, "tier_progress": {"current": goal.current_tier}}

    data = {"goal": notif_goal, "date": str(datetime.utcnow())}
    fcm_ret = send_fcm_notification(change_type, data)
    if fcm_ret["failure"] != 0:
        logger.error("Failed to send FCM message", extra={"fcm_ret": str(fcm_ret)})
    else:
        logger.info("FCM notification sent")


def compare_data(previous, latest):
    for goal in latest:
        previous_goal = next((x for x in previous if x.id == goal.id), None)

        # New goal
        if previous_goal is None:
            logger.info(f"Goal {goal.title} started", extra={"community_goal": goal})
            handle_change("new_goal", goal)
            continue

        # Finished goal
        if goal.is_finished and not previous_goal.is_finished:
            logger.info(f"Goal {goal.title} finished", extra={"community_goal": goal})
            handle_change("finished_goal", goal)
            continue

        # Check if new tier
        if goal.current_tier > previous_goal.current_tier and not goal.is_finished:
            logger.info(
                f"Goal {goal.title} changed tier ({goal.current_tier} from {previous_goal.current_tier})",
                extra={"community_goal": goal},
            )
            handle_change("new_tier", goal)
            continue


def store_updated_data(latest_data, previous_data):
    with get_session(db_engine) as db_session:

        # If no previous store all
        if previous_data is None:
            for item in latest_data:
                db_session.add(item)
            return

        # Else compare to not store bad data
        for item in latest_data:
            previous_item = next((x for x in previous_data if x.id == item.id), None)

            # No previous item, store
            if previous_item is None:
                db_session.add(item)
                continue

            # If previous has bigger tier, don't save new one
            if previous_item.current_tier > item.current_tier:
                continue

            # If previous is finished but now is ongoing, ignore
            if previous_item.is_finished and not item.is_finished:
                continue

            # Else, update
            db_item = (
                db_session.query(CommunityGoalStatus)
                .filter(CommunityGoalStatus.id == item.id)
                .first()
            )
            db_item.id = item.id
            db_item.last_update = item.last_update
            db_item.is_finished = item.is_finished
            db_item.current_tier = item.current_tier
            db_item.title = item.title


def launch_cg_watch():
    logger.info("Checking for CGs changes")

    # First get latest data
    api_data = get_community_goals()
    latest_data = []
    for goal in api_data["goals"]:

        # Get date
        last_update_date = arrow.utcnow()
        if "date" in goal and "last_update" in goal["date"]:
            last_update_date = arrow.get(goal["date"]["last_update"])

        # Get title
        if "title" in goal and len(goal["title"]) != 0:
            title = goal["title"]
        else:
            continue

        latest_data.append(
            CommunityGoalStatus(
                id=goal["id"],
                last_update=last_update_date.datetime,
                is_finished=not goal["ongoing"],
                current_tier=goal["tier_progress"]["current"]
                if "tier_progress" in goal
                else 0,
                title=title,
            )
        )

    if latest_data is None:
        exit(-1)

    # Get previous data from db
    with get_session(db_engine) as db_session:
        previous_data = db_session.query(CommunityGoalStatus).all()

        # If no previous data, write it and exit
        if len(previous_data) == 0:
            store_updated_data(latest_data, None)
            exit(0)

        # Else compare
        compare_data(previous_data, latest_data)

        # Then replace previous
        store_updated_data(latest_data, previous_data)
