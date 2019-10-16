#!/usr/bin/env python3

import json
import time
import zlib

import zmq
from sqlalchemy import create_engine

from config import EDDN_TIMEOUT, EDDN_RELAY, DB_URI
from eddn.eddn_handler import handle_eddn_message


def listen_to_eddn():
    # Create listener
    print("Subscribing to EDDN")
    engine = create_engine(DB_URI)
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, EDDN_TIMEOUT)

    while True:
        try:
            subscriber.connect(EDDN_RELAY)
            print("Subscribed to EDDN")
            while True:
                msg = subscriber.recv()

                if not msg:
                    print("Disconnecting from EDDN")
                    subscriber.disconnect(EDDN_RELAY)
                    break

                msg = zlib.decompress(msg)
                json_msg = json.loads(msg.decode("utf-8"))

                handle_eddn_message(engine, json_msg)
        except Exception as e:
            print("Exception: " + str(e))
            print("Disconnectiing from EDDN due to exception")
            subscriber.disconnect(EDDN_RELAY)
            time.sleep(1)


if __name__ == "__main__":
    listen_to_eddn()
