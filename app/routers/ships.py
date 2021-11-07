from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, Response

from app.models.ships import ShipModel, StationSellingShip
from app.services.ships import ShipsService

router = APIRouter(prefix="/ships", tags=["Ships"])


@router.get(
    "/{ship_model}/picture",
    status_code=307,
    response_class=RedirectResponse,
    responses={307: {}},
)
async def get_ship_picture(
    ship_model: ShipModel, ships_service: ShipsService = Depends()
) -> Response:
    """Redirect to a picture corresponding the ship model.

    Supports both Frontier API ship names (like federation_dropship_mkii) or display names (like Federal Dropship).
    """
    img_path = await ships_service.get_ship_picture_static_path(ship_model)
    return RedirectResponse(img_path)


@router.get("/typeahead", response_model=list[str])
async def get_ships_typeahead(
    input_text: str,
    ships_service: ShipsService = Depends(),
) -> list[str]:
    """Get ships names for autocomplete."""
    return await ships_service.get_ships_typeahead(input_text)


@router.get("/search", response_model=list[StationSellingShip])
async def get_station_selling_ship(
    reference_system: str,
    ship_model: ShipModel,
    ships_service: ShipsService = Depends(),
) -> list[StationSellingShip]:
    """Search for a station selling a specific ship."""
    return await ships_service.get_station_selling_ship(reference_system, ship_model)
