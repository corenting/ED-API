from typing import List

from fastapi import APIRouter, Depends

from app.models.systems import SystemsDistance
from app.routers.helpers.responses import dataclass_response
from app.services.systems import SystemsService

router = APIRouter()


@router.get("/systems/typeahead", tags=["Systems"], response_model=List[str])
async def get_systems_typeahead(
    input_text: str,
    systems_service: SystemsService = Depends(),
) -> List[str]:
    """Get systems names for autocomplete."""
    return await systems_service.get_systems_typeahead(input_text)


@router.get(
    "/systems/distance_calculator", tags=["Systems"], response_model=SystemsDistance
)
@dataclass_response
async def get_systems_distance_calculator(
    first_system: str,
    second_system: str,
    systems_service: SystemsService = Depends(),
) -> SystemsDistance:
    """Get distance between two specified systems."""
    return await systems_service.get_systems_distance_calculator(
        first_system, second_system
    )
