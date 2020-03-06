#!/usr/bin/env python3

import logging
import os

import arrow
import requests
from sqlalchemy import create_engine

from config import DB_URI, WORKING_DIR
from models.database import get_session

logger = logging.getLogger(__name__)


def should_update():
    try:
        response = requests.head("https://eddb.io/archive/v6/listings.csv")
        if response.status_code != 200:
            logger.error("Error while downloading listings update date")
            return False, None

        # Get current date
        current_last_modified = arrow.get(
            response.headers["Last-Modified"], "ddd, DD MMM YYYY HH:mm:ss ZZZ"
        )

        # Get previous date
        try:
            with open(WORKING_DIR + "previous_date", "r") as previous_data:
                file_content = previous_data.read()
                previous_last_modified = arrow.get(file_content)
        except:
            logger.exception("Cannot get previous date", exc_info=True)
            return False, None

        return previous_last_modified < current_last_modified, current_last_modified
    except:
        logger.exception("Error checking update date", exc_info=True)
        return False, None


def write_new_date(curr_last_modified_date):
    try:
        with open(WORKING_DIR + "previous_date", "w+") as text_file:
            print(curr_last_modified_date.isoformat(), file=text_file, end="")
    except Exception as e:
        logger.exception("Cannot write current date", exc_info=True)


def download_file():
    try:
        response = requests.get("https://eddb.io/archive/v6/listings.csv", stream=True)
        if response.status_code != 200:
            logger.error(f"Error {response.status_code} while downloading listings")
            return False

        handle = open(WORKING_DIR + "listings.csv", "wb+")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                handle.write(chunk)
        return True
    except Exception as e:
        logger.exception("Listing import error", exc_info=True)
        return False


def import_db():
    try:
        engine = create_engine(DB_URI)
        with get_session(engine) as session:
            session.execute("TRUNCATE commodities_prices")
            session.execute(
                "COPY commodities_prices FROM '"
                + WORKING_DIR
                + "listings_new.csv' CSV HEADER"
            )
        return True
    except Exception as e:
        logger.exception("DB import error", exc_info=True)
        return False


def adapt_csv():
    try:
        return_code = os.system(
            "cut -d, -f5,9 --complement '"
            + WORKING_DIR
            + "listings.csv' > '"
            + WORKING_DIR
            + "listings_new.csv'"
        )
        return return_code == 0

    except Exception as e:
        logger.exception("CSV modification error", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info(f"Checking for listings update at {arrow.now()}...")
    should_update_listings, current_last_modified_date = should_update()
    if should_update_listings:
        logger.info("Downloading new listings from EDDB...")
        if download_file():
            logger.info("Download complete !")
            logger.info("Removing extra data from CSV...")
            if adapt_csv():
                logger.info("Importing in database...")
                if import_db():
                    write_new_date(current_last_modified_date)
                    logger.info("Importing complete !")
                else:
                    logger.error("Importing error")
        else:
            logger.error("Download error, abort !")
    else:
        logger.info("No listings update required !")
