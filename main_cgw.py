#!/usr/bin/env python3

from pyfcm import FCMNotification
from datetime import datetime
import json
import requests

from config import FCM_API_KEY, WORKING_DIR, DEBUG_MODE

ed_api_url = "https://ed.9cw.eu/v2/community_goals/"

if DEBUG_MODE:
    previous_file_path = "previous.json"
else:
    previous_file_path = WORKING_DIR + "previous.json"

api_key = FCM_API_KEY

push_service = FCMNotification(api_key=api_key)


class DownloadException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def download_json():
    try:
        # Download JSON
        req = requests.get(ed_api_url, headers={'User-Agent': 'EDCGW'})

        if req.status_code != 200:
            raise DownloadException('error ' + str(req.status_code) + ' while downloading community goals')

        json_content = json.loads(req.content.decode("utf-8"))
        req.close()
        return json_content
    except Exception as ex:
        print("Download error (" + str(ex) + ")")
        return None


def store_json(data):
    try:
        with open(previous_file_path, "w") as stored_file:
            stored_file.write(json.dumps(data))
        return True
    except Exception as ex:
        print("Write error (" + str(ex) + ")")
        return False


def send_fcm_notification(topic, data):
    if DEBUG_MODE:
        topic += '_test'
    extra_kwargs = {
        'priority': 'high'
    }

    return push_service.notify_topic_subscribers(topic_name=topic,
                                                 data_message=data,
                                                 extra_kwargs=extra_kwargs,
                                                 collapse_key=data["goal"]["title"],
                                                 time_to_live=86400)


def handle_change(change_type, goal):
    data = {
        'goal': goal,
        'date': str(datetime.utcnow())
    }
    fcm_ret = send_fcm_notification(change_type, data)
    if fcm_ret["failure"] != 0:
        print(' Failed to send FCM message : ' + fcm_ret)
    else:
        print(' FCM notification sent')


def compare_json(previous, latest):
    for goal in latest["goals"]:
        try:
            previous_goal = next((previous_item for previous_item in previous["goals"]
                                  if previous_item["id"] == goal["id"]), None)

            # First check if new goal
            if previous_goal is None:
                print(' Goal "' + goal["title"] + '" started')
                handle_change("new_goal", goal)
                continue

            ongoing_prev = previous_goal["ongoing"]
            ongoing_now = goal["ongoing"]

            # Check if goal finished
            if ongoing_prev and not ongoing_now:
                print(' Goal "' + goal["title"] + '" finished')
                handle_change("finished_goal", goal)
                continue

            tier_prev = previous_goal["tier_progress"]["current"]
            tier_now = goal["tier_progress"]["current"]

            # Check if new tier
            if tier_now > tier_prev and tier_now != 0 and tier_now == tier_prev + 1 and ongoing_now:
                print(' New tier (' + str(tier_now) + ' was ' + str(tier_prev) + ')' + ' for goal "' + goal["title"]
                      + '"')
                handle_change("new_tier", goal)
                continue

        except Exception as e2:
            print(' Error handling a goal : ' + str(e2))
            continue


if __name__ == "__main__":
    print('Looking for CGs changes at ' + str(datetime.now()) + ':')
    # First download latest json
    latest_json = download_json()
    if latest_json is None:
        exit(-1)

    # Open previous one
    try:
        with open(previous_file_path) as previous_data:
            previous_json = json.load(previous_data)
    except Exception as e:
        print(' Cannot open previous json, error (' + str(e) + ')')
        previous_json = None

    # If no previous data, write it and exit
    if previous_json is None:
        store_json(latest_json)
        exit(0)

    # Else compare
    compare_json(previous_json, latest_json)

    # Then replace previous
    store_json(latest_json)
