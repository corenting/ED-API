from fastapi import APIRouter, Depends

from app.models.commodities import Commodity, CommodityPrice
from app.models.exceptions import CommodityNotFoundException
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
    responses={**get_error_response_doc(400, CommodityNotFoundException)},
)
def get_commodity_price(
    commodity: str,
    commodities_service: CommoditiesService = Depends(),
) -> CommodityPrice:
    """Get prices for a specific commodity."""
    return commodities_service.get_commodity_prices(commodity)


@router.get("/prices", response_model=list[CommodityPrice])
def get_commodities_prices(
    commodities_service: CommoditiesService = Depends(),
) -> list[CommodityPrice]:
    """Get all commodities prices."""
    return commodities_service.get_commodities_prices()
