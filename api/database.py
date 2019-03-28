from flask_sqlalchemy import SQLAlchemy

from models.database import database_metadata

db = SQLAlchemy(metadata=database_metadata)


def register_db(app):
    db.app = app
    db.init_app(app)
