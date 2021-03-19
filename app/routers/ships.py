from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, Response

from app.models.exceptions import ShipModelNotFound
from app.models.ships import Ship
from app.routers.helpers.responses import dataclass_response, get_error_response_doc
from app.services.ships import ShipsService

router = APIRouter()


@router.get(
    "/ships/{ship_model}/picture",
    tags=["Ships"],
    status_code=307,
    response_class=RedirectResponse,
    responses={307: {}, **get_error_response_doc(404, ShipModelNotFound)},
)
async def get_ship_picture(
    ship_model: str, ships_service: ShipsService = Depends()
) -> Response:
    """Redirect to a picture corresponding the ship model."""
    try:
        url = (await ships_service.get_ship_model_informations(ship_model)).picture_url
    except ShipModelNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    return RedirectResponse(url)


@router.get(
    "/ships/{ship_model}",
    tags=["Ships"],
    response_model=Ship,
    responses={**get_error_response_doc(404, ShipModelNotFound)},
)
@dataclass_response
async def get_ship_model_informations(
    ship_model: str, ships_service: ShipsService = Depends()
) -> Ship:
    """Get informations about a ship model."""
    try:
        ship = await ships_service.get_ship_model_informations(ship_model)
    except ShipModelNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    return ship


@router.get(
    "/ships",
    tags=["Ships"],
    response_model=List[Ship],
)
@dataclass_response
async def get_all_ships(ships_service: ShipsService = Depends()) -> List[Ship]:
    """Get list of ship models."""
    return await ships_service.get_all_ships()
