import json

import requests

from api.helpers.request import get_requests_headers
from models.database import (
    BlueprintEngineerLink,
    BlueprintIngredientLink,
    EngineerBlueprint,
    Engineer,
    BlueprintIngredient,
)
from models.internal.import_exception import ImportException


def import_blueprints(db_session):
    try:
        print("Blueprints imports started")

        # First remove existing data
        db_session.query(BlueprintEngineerLink).delete()
        db_session.query(BlueprintIngredientLink).delete()
        db_session.query(EngineerBlueprint).delete()
        db_session.query(Engineer).delete()
        db_session.query(BlueprintIngredient).delete()

        # Download JSON
        req = requests.get(
            "https://raw.githubusercontent.com/msarilar/EDEngineer/master/EDEngineer/Resources/Data"
            "/blueprints.json",
            headers=get_requests_headers(),
        )

        if req.status_code != 200:
            raise ImportException(
                "Error " + str(req.status_code) + " while downloading blueprints.json"
            )

        body = req.content
        j = json.loads(body.decode("utf-8-sig"))
        req.close()

        # First loop to add other tables (engineers...)
        engineers_list = []
        ingredients_list = []
        for item in j:
            engineers_array = item["Engineers"]
            ingredients_array = item["Ingredients"]

            # Engineers
            for eng in engineers_array:
                engineer = Engineer(name=eng)
                if not any(
                    db_engineer.name == engineer.name for db_engineer in engineers_list
                ):
                    engineers_list.append(engineer)
                    db_session.add(engineer)

            # Blueprint ingredients
            for ingredient in ingredients_array:
                ingredient = BlueprintIngredient(name=ingredient["Name"])
                if not any(
                    db_ingredient.name == ingredient.name
                    for db_ingredient in ingredients_list
                ):
                    ingredients_list.append(ingredient)
                    db_session.add(ingredient)

        db_session.flush()

        # Second loop to add the blueprints themselves and the association tables
        for item in j:
            grade = item["Grade"] if "Grade" in item else None
            new_blueprint = EngineerBlueprint(
                name=item["Name"], type=item["Type"], grade=grade
            )
            ingredients_array = item["Ingredients"]
            engineers_array = item["Engineers"]
            for ingredient in ingredients_array:
                db_ingredient = next(
                    (x for x in ingredients_list if x.name == ingredient["Name"]), None
                )
                ingredient_link = BlueprintIngredientLink(
                    blueprint=new_blueprint,
                    ingredient=db_ingredient,
                    quantity=ingredient["Size"],
                )
                db_session.add(ingredient_link)
            for engineer in engineers_array:
                db_engineer = next(
                    (x for x in engineers_list if x.name == engineer), None
                )
                engineer_link = BlueprintEngineerLink(
                    blueprint=new_blueprint, engineer=db_engineer
                )
                db_session.add(engineer_link)

        db_session.commit()
        print("Blueprints import finished")
        return True
    except Exception as e:
        print("Blueprints import error (" + str(e) + ")")
        db_session.rollback()
        return False
