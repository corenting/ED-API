import arrow
from flask.json import JSONEncoder

from models.database import (
    Commodity,
    CommodityPrice,
    CommodityCategory,
    EngineerBlueprint,
    BlueprintEngineerLink,
    BlueprintIngredientLink,
    System,
    Ship,
    StationShipLink,
    Station,
    StationModuleLink,
)


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj):

        # Try objet get_api_model method
        object_get_api_model = getattr(obj, "get_api_model", None)
        if callable(object_get_api_model):
            return object_get_api_model()

        if isinstance(obj, EngineerBlueprint):
            return {
                "name": obj.name,
                "type": obj.type,
                "grade": obj.grade,
                "engineers": obj.engineers,
                "ingredients": obj.ingredients,
            }
        if isinstance(obj, BlueprintEngineerLink):
            return obj.engineer.name
        if isinstance(obj, BlueprintIngredientLink):
            return {"name": obj.ingredient.name, "quantity": obj.quantity}
        if isinstance(obj, System):
            return {
                "id": obj.id,
                "name": obj.name,
                "permit_required": obj.permit_required,
                "x": obj.x,
                "y": obj.y,
                "z": obj.z,
            }
        if isinstance(obj, Ship):
            return {"name": obj.name}
        if isinstance(obj, StationShipLink):
            return obj.ship.name
        if isinstance(obj, StationModuleLink):
            return {
                "id": obj.module.id,
                "class": obj.module.module_class,
                "rating": obj.module.rating,
                "group": obj.module.group.name,
            }
        if isinstance(obj, Station):
            return {
                "id": obj.id,
                "name": obj.name,
                "is_planetary": obj.is_planetary,
                "is_fleet_carrier": obj.type == "Fleet Carrier",
                "last_shipyard_update": arrow.get(obj.last_shipyard_update).isoformat(),
                "distance_to_star": obj.distance_to_star,
                "max_landing_pad": obj.max_landing_pad
                if obj.max_landing_pad is not None
                else "Unknown",
                "type": obj.type,
                "system": obj.system,
            }
        return super(CustomJsonEncoder, self).default(obj)
