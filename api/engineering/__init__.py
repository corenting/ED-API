from flask import Blueprint, jsonify

from api.extensions.database import db
from models.database import Engineer, EngineerBlueprint

engineering_bp = Blueprint("engineering", __name__)


@engineering_bp.route("/blueprints/")
def flask_get_blueprints():
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
    return jsonify(blueprints)


@engineering_bp.route("/synthesis/")
def flask_get_synthesis():
    return jsonify(get_specific_blueprints_list("@Synthesis"))


@engineering_bp.route("/technology/")
def flask_get_technology():
    return jsonify(get_specific_blueprints_list("@Technology"))


@engineering_bp.route("/engineers/")
def flask_get_engineers():
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
    return jsonify(ret_list)


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
