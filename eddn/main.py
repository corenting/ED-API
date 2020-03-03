import json
import logging
import time
import zlib

import zmq
from sqlalchemy import create_engine

from config import EDDN_TIMEOUT, EDDN_RELAY, DB_URI
from eddn.handler import handle_eddn_message

logger = logging.getLogger(__name__)


def listen_to_eddn():
    # Create listener
    logger.debug("Subscribing to EDDN")
    engine = create_engine(DB_URI)
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, EDDN_TIMEOUT)

    while True:
        try:
            subscriber.connect(EDDN_RELAY)
            logger.debug("Subscribed to EDDN")
            while True:
                msg = subscriber.recv()

                if not msg:
                    raise Exception("No message from EDDN")

                msg = zlib.decompress(msg)
                json_msg = json.loads(msg.decode("utf-8"))
                logger.debug("Received EDDN message", extra={"eddn_message": json_msg})

                handle_eddn_message(engine, json_msg)
        except:
            logger.exception("Disconnected from EDDN", exc_info=True)
            subscriber.disconnect(EDDN_RELAY)
            time.sleep(1)
