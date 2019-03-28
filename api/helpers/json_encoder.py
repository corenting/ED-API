import arrow

from flask.json import JSONEncoder

from models.database import Commodity, CommodityPrice, CommodityCategory, EngineerBlueprint, BlueprintEngineerLink, \
    BlueprintIngredientLink, System, Ship, StationShipLink, Station


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Commodity):
            return {
                'id': obj.id,
                'name': obj.name,
                'average_price': obj.average_price,
                'is_rare': obj.is_rare,
                'category': obj.category,
            }
        if isinstance(obj, CommodityPrice):
            return {
                'commodity': obj.commodity,
                'supply': obj.supply,
                'buy_price': obj.buy_price,
                'sell_price': obj.sell_price,
                'demand': obj.demand,
                'collected_at': arrow.get(obj.collected_at).isoformat(),
            }
        if isinstance(obj, CommodityCategory):
            return {
                'id': obj.id,
                'name': obj.name,
            }
        if isinstance(obj, EngineerBlueprint):
            return {
                'name': obj.name,
                'type': obj.type,
                'grade': obj.grade,
                'engineers': obj.engineers,
                'ingredients': obj.ingredients,
            }
        if isinstance(obj, BlueprintEngineerLink):
            return obj.engineer.name
        if isinstance(obj, BlueprintIngredientLink):
            return {
                'name': obj.ingredient.name,
                'quantity': obj.quantity,
            }
        if isinstance(obj, System):
            return {
                'id': obj.id,
                'name': obj.name,
                'permit_required': obj.permit_required,
                'x': obj.x,
                'y': obj.y,
                'z': obj.z,
            }
        if isinstance(obj, Ship):
            return {
                'name': obj.name
            }
        if isinstance(obj, StationShipLink):
            return obj.ship.name
        if isinstance(obj, Station):
            return {
                'id': obj.id,
                'name': obj.name,
                'is_planetary': obj.is_planetary,
                'last_shipyard_update': arrow.get(obj.last_shipyard_update).isoformat(),
                'distance_to_star': obj.distance_to_star,
                'max_landing_pad': obj.max_landing_pad if obj.max_landing_pad is not None else "Unknown",
                'type': obj.type,
                'system': obj.system,
                'ships_sold': obj.ships_sold
            }
        return super(CustomJsonEncoder, self).default(obj)
