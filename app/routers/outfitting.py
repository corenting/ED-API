from fastapi import APIRouter, Depends

from app.services.outfitting import OutfittingService

router = APIRouter(prefix="/outfitting", tags=["Outfitting"])


@router.get("/typeahead", response_model=list[str])
async def get_outfitting_typeahead(
    input_text: str,
    outfitting_service: OutfittingService = Depends(),
) -> list[str]:
    """Get outfitting items names for autocomplete."""
    return outfitting_service.get_outfitting_typeahead(input_text)
