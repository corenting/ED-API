from app.constants import STATIC_PATH
from app.models.ships import SHIP_NAMES, ShipModel


class ShipsService:
    """Main class for the ships service."""

    async def get_ship_picture_static_path(self, ship_model: ShipModel) -> str:
        """Get the static path to a ship picture."""
        return f"/{STATIC_PATH}/images/ships/{ship_model.value}.png"

    async def get_ships_typeahead(self, input_text: str) -> list[str]:
        """Get ships names for autocomplete."""
        return [
            item for item in SHIP_NAMES if item.lower().startswith(input_text.lower())
        ]
