from fastapi import APIRouter, Depends

from app.models.commodities import Commodity, CommodityPrice
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


@router.get("/prices", response_model=list[CommodityPrice])
def get_commodities_prices(
    commodities_service: CommoditiesService = Depends(),
) -> list[CommodityPrice]:
    """Get all commodities prices."""
    return commodities_service.get_commodities_prices()
