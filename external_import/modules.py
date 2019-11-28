import json

import requests
from sqlalchemy import create_engine

from api.helpers.request import get_requests_headers
from config import DB_URI
from models.database import (
    get_session,
    Module,
    ModuleGroup,
)
from models.internal.import_exception import ImportException



if __name__ == "__main__":
    db_engine = create_engine(DB_URI)
    with get_session(db_engine) as sess:
        import_modules(sess)
