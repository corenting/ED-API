import json
from urllib.parse import quote

import requests

from api.helpers.request import get_requests_headers
from models.database import System
import logging

logger = logging.getLogger(__name__)


def get_factions(name, include_history=False):
    try:
        # Download JSON
        url = "https://www.edsm.net/api-system-v1/factions?systemName=" + quote(name)
        if include_history is not None and include_history:
            url += "&showHistory=1"
        req = requests.get(url, headers=get_requests_headers())

        if req.status_code != 200:
            logger.error(f"Error getting factions from EDSM (HTTP {req.status_code})")
            return None

        body = req.content
        j = json.loads(body.decode("utf-8"))
        req.close()

        return j
    except:
        logger.exception("Exception getting factions from EDSM", exc_info=True)
        return None


def get_system(name):
    try:
        # Download JSON
        url = (
            "https://www.edsm.net/api-v1/systems?showPermit=1&showId=1&showCoordinates=1&systemName="
            + quote(name)
        )
        req = requests.get(url, headers=get_requests_headers())

        if req.status_code != 200:
            logger.error(f"Error getting system from EDSM (HTTP {req.status_code})")
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
    except:
        logger.exception("Exception getting system from EDSM", exc_info=True)
        return None
