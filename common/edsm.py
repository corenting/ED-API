import json
from urllib.parse import quote

import requests

from api.helpers.request import get_requests_headers
from models.database import System


def get_factions_from_edsm(name, include_history=False):
    try:
        # Download JSON
        url = "https://www.edsm.net/api-system-v1/factions?systemName=" + quote(name)
        if include_history is not None and include_history:
            url += "&showHistory=1"
        req = requests.get(url, headers=get_requests_headers())

        if req.status_code != 200:
            print("Request failure " + req.status_code)
            return None

        body = req.content
        j = json.loads(body.decode("utf-8"))
        req.close()

        return j
    except Exception as e:
        print("Request exception " + str(e))
        return None


def get_system_from_edsm(name):
    try:
        # Download JSON
        url = (
            "https://www.edsm.net/api-v1/systems?showPermit=1&showId=1&showCoordinates=1&systemName="
            + quote(name)
        )
        req = requests.get(url, headers=get_requests_headers())

        if req.status_code != 200:
            print("Request failure " + req.status_code)
            return None

        body = req.content
        j = json.loads(body.decode("utf-8"))[0]
        req.close()
        return System(
            id=j["id"],
            x=j["coords"]["x"],
            y=j["coords"]["y"],
            z=j["coords"]["z"],
            name=j["name"],
            permit_required=j["requirePermit"],
        )
    except Exception as e:
        print("Request exception " + str(e))
        return None
