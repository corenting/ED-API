from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.models.exceptions import SystemNotFoundError
from app.models.stations import StationDetails
from app.models.systems import SystemDetails, SystemFactionHistory, SystemsDistance
from app.routers.helpers.responses import get_error_response_doc
from app.services.systems import SystemsService

router = APIRouter(prefix="/systems", tags=["Systems"])


@router.get("/typeahead", response_model=list[str])
async def get_systems_typeahead(
    input_text: str,
    systems_service: SystemsService = Depends(),
) -> list[str]:
    """Get systems names for autocomplete."""
    return await systems_service.get_systems_typeahead(input_text)


@router.get(
    "/distance_calculator",
    response_model=SystemsDistance,
    responses={**get_error_response_doc(400, SystemNotFoundError)},
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
    except SystemNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e


@router.get(
    "/{system_name}",
    response_model=SystemDetails,
    responses={**get_error_response_doc(400, SystemNotFoundError)},
)
async def get_system_details(
    system_name: str,
    systems_service: SystemsService = Depends(),
) -> SystemDetails:
    """Get details of a specified system."""
    try:
        return await systems_service.get_system_details(system_name)
    except SystemNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e


@router.get(
    "/{system_name}/stations",
    response_model=list[StationDetails],
    responses={**get_error_response_doc(400, SystemNotFoundError)},
)
async def get_system_stations(
    system_name: str,
    systems_service: SystemsService = Depends(),
) -> list[StationDetails]:
    """Get details of a specified system."""
    try:
        return await systems_service.get_system_stations(system_name)
    except SystemNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e


@router.get(
    "/{system_name}/factions_history",
    response_model=list[SystemFactionHistory],
    responses={**get_error_response_doc(400, SystemNotFoundError)},
)
async def get_system_factions_history(
    system_name: str,
    systems_service: SystemsService = Depends(),
) -> list[SystemFactionHistory]:
    """Get factions history for a specified system."""
    try:
        return await systems_service.get_system_factions_history(system_name)
    except SystemNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e
