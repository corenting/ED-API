import csv
import json
from io import StringIO

import requests
from sqlalchemy import create_engine

from api.database import db
from api.helpers.request import get_requests_headers
from config import DB_URI
from models.database import Commodity, CommodityCategory, get_session, Module, ModuleGroup
from models.internal.import_exception import ImportException


def import_modules(db_session):
    try:
        print('Modules import started')
        # First remove existing data
        db_session.query(Module).delete()
        db_session.query(ModuleGroup).delete()

        # Download JSON
        req = requests.get('https://eddb.io/archive/v6/modules.json',
                           headers=get_requests_headers())

        if req.status_code != 200:
            raise ImportException('Error ' + str(req.status_code) + ' while downloading modules.json')

        body = req.content
        eddb_json = json.loads(body.decode("utf-8"))
        req.close()

        # First loop to add modules groups
        modules_groups = []
        for module in eddb_json:
            group = ModuleGroup(id=module["group"]["id"], category_id=module["group"]["category_id"],
                                name=module["group"]["name"], category=module["group"]['category'])
            if not any(db_module.id == group.id for db_module in modules_groups):
                modules_groups.append(group)
        for module in modules_groups:
            db_session.add(module)

        # Second loop to add the modules themselves
        for module in eddb_json:
            item = Module(id=module['id'], module_class=module['class'], rating=module['rating'], price=module['price'],
                          group_id=module['group_id'])
            db_session.add(item)
        db_session.commit()
        print('Modules import finished')
        return True
    except Exception as e:
        print("Modules import error (" + str(e) + ")")
        db_session.rollback()
        return False


if __name__ == '__main__':
    db_engine = create_engine(DB_URI)
    with get_session(db_engine) as sess:
        import_modules(sess)
