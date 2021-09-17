from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.models.exceptions import SystemNotFoundException
from app.models.stations import Station
from app.models.systems import SystemDetails, SystemsDistance
from app.routers.helpers.responses import get_error_response_doc
from app.services.systems import SystemsService

router = APIRouter()


@router.get("/systems/typeahead", tags=["Systems"], response_model=list[str])
async def get_systems_typeahead(
    input_text: str,
    systems_service: SystemsService = Depends(),
) -> list[str]:
    """Get systems names for autocomplete."""
    return await systems_service.get_systems_typeahead(input_text)


@router.get(
    "/systems/distance_calculator",
    tags=["Systems"],
    response_model=SystemsDistance,
    responses={**get_error_response_doc(400, SystemNotFoundException)},
)
async def get_systems_distance_calculator(
    first_system: str,
    second_system: str,
    systems_service: SystemsService = Depends(),
) -> SystemsDistance:
    """Get distance between two specified systems."""
    try:
        return await systems_service.get_systems_distance_calculator(
            first_system, second_system
        )
    except SystemNotFoundException as e:
        raise HTTPException(status_code=400, detail=e.error_code)


@router.get(
    "/systems/{system_name}",
    tags=["Systems"],
    response_model=SystemDetails,
    responses={**get_error_response_doc(400, SystemNotFoundException)},
)
async def get_systems_details(
    system_name: str,
    systems_service: SystemsService = Depends(),
) -> SystemDetails:
    """Get details of a specified system."""
    try:
        return await systems_service.get_system_details(system_name)
    except SystemNotFoundException as e:
        raise HTTPException(status_code=400, detail=e.error_code)


@router.get(
    "/systems/{system_name}/stations",
    tags=["Systems"],
    response_model=list[Station],
    responses={**get_error_response_doc(400, SystemNotFoundException)},
)
async def get_systems_stations(
    system_name: str,
    systems_service: SystemsService = Depends(),
) -> list[Station]:
    """Get details of a specified system."""
    try:
        return await systems_service.get_system_stations(system_name)
    except SystemNotFoundException as e:
        raise HTTPException(status_code=400, detail=e.error_code)
