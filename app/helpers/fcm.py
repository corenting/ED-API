from typing import Any

from pyfcm import FCMNotification

from app.config import DEBUG, FCM_API_KEY

push_service = FCMNotification(api_key=FCM_API_KEY)


def send_fcm_notification(topic: str, collapse_key: str, data_message: dict) -> dict:
    """Send a FCM notification."""
    if DEBUG:
        topic += "_test"

    return push_service.notify_topic_subscribers(
        topic_name=topic,
        data_message=data_message,
        extra_kwargs={"priority": "high"},
        collapse_key=collapse_key,
        time_to_live=86400,
    )
