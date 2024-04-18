from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.models.commodities import (
    BestPricesStations,
    Commodity,
    CommodityPrice,
    FindCommodityMode,
    StationWithCommodityDetails,
)
from app.models.exceptions import CommodityNotFoundError
from app.models.stations import StationLandingPadSize
from app.routers.helpers.responses import get_error_response_doc
from app.services.commodities import CommoditiesService

router = APIRouter(prefix="/commodities", tags=["Commodities"])


@router.get("/typeahead", response_model=list[str])
def get_commodities_typeahead(
    input_text: str,
    commodities_service: CommoditiesService = Depends(),
) -> list[str]:
    """Get commodities names for autocomplete."""
    return commodities_service.get_commodities_typeahead(input_text)


@router.get("", response_model=list[Commodity])
def get_commodities(
    commodities_service: CommoditiesService = Depends(),
) -> list[Commodity]:
    """Get all commodities."""
    return commodities_service.get_commodities()


@router.get(
    "/{commodity}/prices",
    response_model=CommodityPrice,
    responses={**get_error_response_doc(400, CommodityNotFoundError)},
)
def get_commodity_price(
    commodity: str,
    commodities_service: CommoditiesService = Depends(),
) -> CommodityPrice:
    """Get prices for a specific commodity."""
    try:
        return commodities_service.get_commodity_prices(commodity)
    except CommodityNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e


@router.get(
    "/{commodity}/best_prices",
    response_model=BestPricesStations,
    responses={**get_error_response_doc(400, CommodityNotFoundError)},
)
async def get_where_to_sell_commodity(
    commodity: str,
    max_age_days: int = 7,
    commodities_service: CommoditiesService = Depends(),
) -> BestPricesStations:
    """Get the best stations to buy or sell a specific commodity.

    Will only include prices from stations where market prices where updates between now
    and now - max_age_days.
    """
    try:
        return await commodities_service.get_stations_with_best_prices_for_commodity(
            commodity, max_age_days
        )
    except CommodityNotFoundError as e:
        raise HTTPException(status_code=400, detail=e.error_code) from e


@router.get(
    "/prices",
    response_model=list[CommodityPrice],
    responses={**get_error_response_doc(400, CommodityNotFoundError)},
)
def get_commodities_prices(
    commodities_service: CommoditiesService = Depends(),
    filter: str | None = None,
) -> list[CommodityPrice]:
    """Get all commodities prices (with an optional filter) ."""
    return commodities_service.get_commodities_prices(filter)


@router.get("/find", response_model=list[StationWithCommodityDetails])
async def find_commodity(
    mode: FindCommodityMode,
    reference_system: str,
    commodity: str,
    min_landing_pad_size: StationLandingPadSize,
    min_quantity: int,
    max_age_days: int = 7,
    commodities_service: CommoditiesService = Depends(),
) -> list[StationWithCommodityDetails]:
    """Get stations buying or selling a specific commodity near a reference system.

    Only works for non-rare commodities.
    Will only include prices from stations where market prices where updates between now
    and now - max_age_days.
    """
    return await commodities_service.find_commodity(
        mode,
        reference_system,
        commodity,
        min_landing_pad_size,
        min_quantity,
        max_age_days,
    )
