import logging

from eddn.utils import get_station_by_names, get_price
from models.database import get_session

SCHEMA_REF = "$schemaRef"
COMMODITY_SCHEMA = "https://eddn.edcd.io/schemas/commodity/3"
logger = logging.getLogger(__name__)


def handle_eddn_message(db_engine, data):
    """
    Process an update from EDDN
    :param db_engine: sql alchemy db engine
    :param data: the message data
    :return:
    """
    if data:
        if data.get(SCHEMA_REF, "") == COMMODITY_SCHEMA:
            star_name = data["message"]["systemName"]
            station_name = data["message"]["stationName"]
            with get_session(db_engine) as session:
                station = get_station_by_names(session, star_name, station_name)
                if station:
                    # go through all the commodities and update prices
                    for item in data["message"]["commodities"]:
                        try:
                            price = get_price(session, station.id, item["name"])
                            if price:
                                price.from_eddn_dict(data["message"]["timestamp"], item)
                        except:
                            logger.exception(
                                "Failed to update price",
                                extra={"eddn_message": data["message"]},
                                exc_info=True,
                            )
