from fastapi import APIRouter, Depends, HTTPException

from app.models.exceptions import OutfittingNotFoundError
from app.models.outfitting import StationWithOutfittingDetails
from app.models.stations import StationLandingPadSize
from app.routers.helpers.responses import get_error_response_doc
from app.services.outfitting import OutfittingService

router = APIRouter(prefix="/outfitting", tags=["Outfitting"])


@router.get("/typeahead", response_model=list[str])
async def get_outfitting_typeahead(
    input_text: str,
    outfitting_service: OutfittingService = Depends(),
) -> list[str]:
    """Get outfitting items names for autocomplete."""
    return outfitting_service.get_outfitting_typeahead(input_text)


@router.get("/find", response_model=list[StationWithOutfittingDetails], responses={**get_error_response_doc(400, OutfittingNotFoundError)},)
async def find_outfitting(
    reference_system: str,
    outfitting: str,
    min_landing_pad_size: StationLandingPadSize,
    max_age_days: int = 7,
    outfitting_service: OutfittingService = Depends(),
) -> list[StationWithOutfittingDetails]:
    """Get stations buying or selling a specific outfitting near a reference system.

    Will only include prices from stations where outfitting prices where updates between now
    and now - max_age_days.
    """
    try:
        return await outfitting_service.find_outfitting(
            reference_system,
            outfitting,
            min_landing_pad_size,
            max_age_days,
        )
    except OutfittingNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e
