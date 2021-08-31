from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, Response

from app.models.ships import ShipModel
from app.services.ships import ShipsService

router = APIRouter()


@router.get(
    "/ships/{ship_model}/picture",
    tags=["Ships"],
    status_code=307,
    response_class=RedirectResponse,
    responses={307: {}},
)
async def get_ship_picture(
    ship_model: ShipModel, ships_service: ShipsService = Depends()
) -> Response:
    """Redirect to a picture corresponding the ship model."""
    img_path = await ships_service.get_ship_picture_static_path(ship_model)
    return RedirectResponse(img_path)
