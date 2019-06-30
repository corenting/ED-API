import csv
import json
from io import StringIO

import requests
from sqlalchemy import create_engine

from api.database import db
from api.helpers.request import get_requests_headers
from config import DB_URI
from models.database import Commodity, CommodityCategory, get_session
from models.internal.import_exception import ImportException


def import_commodities(db_session):
    try:
        print('Commodities import started')
        # First remove existing data
        db_session.query(Commodity).delete()
        db_session.query(CommodityCategory).delete()

        # Download JSON
        req = requests.get('https://eddb.io/archive/v6/commodities.json',
                           headers=get_requests_headers())

        if req.status_code != 200:
            raise ImportException('Error ' + str(req.status_code) + ' while downloading commodities.json')

        body = req.content
        eddb_json = json.loads(body.decode("utf-8"))
        req.close()

        # Download CSV of names
        req = requests.get('https://raw.githubusercontent.com/EDCD/FDevIDs/master/commodity.csv',
                           headers=get_requests_headers())

        if req.status_code != 200:
            raise ImportException('Error ' + str(req.status_code) + ' while downloading commodity.csv')

        body = req.content
        csv_results = []
        csv_file = StringIO(str(body.decode("utf-8")))
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:  # each row is a list
            csv_results.append(row)
        csv_file.close()
        req.close()

        # First loop to add commodities categories
        categories_list = []
        for commodity in eddb_json:
            category = CommodityCategory(id=commodity["category"]["id"], name=commodity["category"]["name"])
            if not any(db_cat.id == category.id for db_cat in categories_list):
                categories_list.append(category)
        for cat in categories_list:
            db_session.add(cat)

        # Second loop to add the commodities themselves
        for commodity in eddb_json:
            csv_commodity = next((x for x in csv_results if int(x['id']) == int(commodity['ed_id'])), None)
            if csv_commodity is None:
                internal_name = commodity['name']
            else:
                internal_name = csv_commodity['symbol']
            item = Commodity(id=commodity["id"], name=commodity["name"], internal_name=internal_name,
                             average_price=commodity["average_price"], is_rare=bool(commodity["is_rare"]),
                             category_id=commodity["category_id"])
            db_session.add(item)
        db_session.commit()
        print('Commodities import finished')
        return True
    except Exception as e:
        print("Commodities import error (" + str(e) + ")")
        db_session.rollback()
        return False


if __name__ == '__main__':
    db_engine = create_engine(DB_URI)
    with get_session(db_engine) as sess:
        import_commodities(sess)
