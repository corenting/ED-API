from flask import Blueprint

from api.database import db
from api.helpers.response import get_response
from models.database import Engineer, EngineerBlueprint

engineering_bp = Blueprint("engineering", __name__)


@engineering_bp.route("/blueprints/")
def flask_get_blueprints():
    return get_response(get_blueprints_list())


@engineering_bp.route("/synthesis/")
def flask_get_synthesis():
    return get_response(get_specific_blueprints_list("@Synthesis"))


@engineering_bp.route("/technology/")
def flask_get_technology():
    return get_response(get_specific_blueprints_list("@Technology"))


@engineering_bp.route("/engineers/")
def flask_get_engineers():
    return get_response(get_engineers_list())


def get_blueprints_list():
    blueprints = (
        db.session.query(EngineerBlueprint)
        .filter(~EngineerBlueprint.type.ilike("Unlock"))
        .all()
    )
    blueprints = [
        x
        for x in blueprints
        if not any(eng.engineer.name == "@Synthesis" for eng in x.engineers)
        and not any(eng.engineer.name == "@Technology" for eng in x.engineers)
    ]
    return blueprints


def get_specific_blueprints_list(type_name):
    blueprints = (
        db.session.query(EngineerBlueprint)
        .filter(~EngineerBlueprint.type.ilike("Unlock"))
        .all()
    )
    blueprints = [
        x
        for x in blueprints
        if any(eng.engineer.name == type_name for eng in x.engineers)
    ]
    return blueprints


def get_engineers_list():
    engineers = (
        db.session.query(Engineer)
        .filter(~Engineer.name.ilike("@Technology"), ~Engineer.name.ilike("@Synthesis"))
        .all()
    )
    unlock_conditions = (
        db.session.query(EngineerBlueprint)
        .filter(EngineerBlueprint.type.ilike("Unlock"))
        .all()
    )
    ret_list = []
    for engineer in engineers:
        unlock_condition = next(
            (x for x in unlock_conditions if x.name == engineer.name), None
        )
        ret_list.append(
            {
                "name": engineer.name,
                "unlock_items": None
                if unlock_condition is None
                else unlock_condition.ingredients,
            }
        )
    return ret_list
