from firebase_admin import exceptions, initialize_app, messaging

from app.config import DEBUG
from loguru import logger

default_app = initialize_app()


def send_fcm_notification(topic: str, collapse_key: str, data_message: dict) -> bool:
    """Send a FCM notification."""
    if DEBUG:
        topic += "_test"

    message = messaging.Message(
        data=data_message,
        topic=topic,
        android=messaging.AndroidConfig(
            ttl=86400, priority="high", collapse_key=collapse_key
        ),
    )

    try:
        messaging.send(message)
        return True
    except exceptions.FirebaseError:
        logger.error("Error while sending FCM message", exc_info=True)
        return False
