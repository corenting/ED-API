import json

import requests

from api.helpers.request import get_requests_headers
from models.database import Commodity, CommodityCategory
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
        j = json.loads(body.decode("utf-8"))
        req.close()

        # First loop to add commodities categories
        categories_list = []
        for c in j:
            category = CommodityCategory(id=c["category"]["id"], name=c["category"]["name"])
            if not any(db_cat.id == category.id for db_cat in categories_list):
                categories_list.append(category)
        for cat in categories_list:
            db_session.add(cat)

        # Second loop to add the commodities themselves
        for c in j:
            item = Commodity(id=c["id"], name=c["name"], average_price=c["average_price"], is_rare=bool(c["is_rare"]),
                             category_id=c["category_id"])
            db_session.add(item)
        db_session.commit()
        print('Commodities import finished')
        return True
    except Exception as e:
        print("Commodities import error (" + str(e) + ")")
        db_session.rollback()
        return False
