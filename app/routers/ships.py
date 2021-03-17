from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, Response

from app.models.exceptions import ShipModelNotFound
from app.routers.helpers.responses import get_error_response_doc
from app.services.ships import ShipsService

router = APIRouter()


@router.get(
    "/ships/{ship_model}/picture",
    tags=["Ships"],
    status_code=307,
    response_class=RedirectResponse,
    responses={307: {}, **get_error_response_doc(404, ShipModelNotFound)},
)
async def get_ship_picture(ship_model: str) -> Response:
    """Redirect to a picture corresponding the ship model."""
    try:
        url = await ShipsService().get_picture_uri(ship_model)
    except ShipModelNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    return RedirectResponse(url)
