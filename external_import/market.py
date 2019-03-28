#!/usr/bin/env python3

import requests
import arrow
import os

from sqlalchemy import create_engine

from config import WORKING_DIR, DB_URI
from models.database import get_session


def should_update():
    try:
        response = requests.head('https://eddb.io/archive/v6/listings.csv')
        if response.status_code != 200:
            print('    Error while downloading listings update date')
            return False, None

        # Get current date
        current_last_modified = arrow.get(response.headers["Last-Modified"], 'ddd, DD MMM YYYY HH:mm:ss ZZZ')

        # Get previous date
        try:
            with open(WORKING_DIR + 'previous_date', 'r') as previous_data:
                file_content = previous_data.read()
                previous_last_modified = arrow.get(file_content)
        except Exception as e:
            print('    Cannot get previous date, error (' + str(e) + ')')
            return False, None

        return previous_last_modified < current_last_modified, current_last_modified
    except Exception as e:
        print("    Error checking update date (" + str(e) + ")")
        return False, None


def write_new_date(curr_last_modified_date):
    try:
        with open(WORKING_DIR + 'previous_date', 'w+') as text_file:
            print(curr_last_modified_date.isoformat(), file=text_file, end='')
    except Exception as e:
        print('    Cannot write current date, error (' + str(e) + ')')


def download_file():
    try:
        response = requests.get('https://eddb.io/archive/v6/listings.csv', stream=True)
        if response.status_code != 200:
            print('    Error while downloading listings')
            return False

        handle = open(WORKING_DIR + 'listings.csv', "wb+")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                handle.write(chunk)
        return True
    except Exception as e:
        print("    Listing import error (" + str(e) + ")")
        return False


def import_db():
    try:
        engine = create_engine(DB_URI)
        with get_session(engine) as session:
            session.execute('TRUNCATE commodities_prices')
            session.execute("COPY commodities_prices FROM '" + WORKING_DIR + "listings_new.csv' CSV HEADER")
        return True
    except Exception as e:
        print("    Db import error (" + str(e) + ")")
        return False


def adapt_csv():
    try:
        return_code = os.system(
            "cut -d, -f5,9 --complement '" + WORKING_DIR + "listings.csv' > '" + WORKING_DIR + "listings_new.csv'")
        return return_code == 0

    except Exception as e:
        print("    Csv adapt error (" + str(e) + ")")
        return False


if __name__ == "__main__":
    print('Checking for listings update at ' + str(arrow.now()) + '...')
    should_update_listings, current_last_modified_date = should_update()
    if should_update_listings:
        print('Downloading new listings from EDDB...')
        if download_file():
            print('Download complete !')
            print('Removing extra data from CSV...')
            if adapt_csv():
                print('Importing in database...')
                if import_db():
                    write_new_date(current_last_modified_date)
                print('Import complete !')
        else:
            print('Download error, abort !')
    else:
        print('No listings update required !')
