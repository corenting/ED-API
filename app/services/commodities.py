import csv
import datetime
import difflib
from typing import Any

import httpx
from bs4 import BeautifulSoup
from cachier import cachier
from dateutil.parser import parse

from app.constants import DATA_PATH, SPANSH_STATIONS_SEARCH_URL
from app.helpers.httpx import get_async_httpx_client, get_httpx_client
from app.helpers.string import string_to_int
from app.models.commodities import (
    BestPricesStations,
    Commodity,
    CommodityPrice,
    FindCommodityMode,
    StationWithCommodityDetails,
)
from app.models.exceptions import CommodityNotFoundError, ContentFetchingError
from app.models.stations import StationLandingPadSize
from app.services.helpers.fleet_carriers import is_fleet_carrier
from app.services.helpers.settlements import is_settlement
from app.services.helpers.spansh import (
    get_max_age_values_for_request_body,
    get_request_body_common_filters,
    get_station_max_landing_pad_size,
)

SPANSH_COMMODITIES_TYPEAHEAD_SERVICE_URL = (
    "https://spansh.co.uk/api/stations/field_values/market"
)
INARA_COMMODITIES = "https://inara.cz/elite/commodities-list/"


def _get_commodity_from_name(
    name: str, commodities: list[Commodity]
) -> Commodity | None:
    """Get the commodity with the specified name using difflib for handling small differences."""
    match = difflib.get_close_matches(name, [x.name for x in commodities])
    if match is None or len(match) == 0:
        return None

    valid_name = match[0]
    return next(x for x in commodities if x.name == valid_name)


@cachier(stale_after=datetime.timedelta(minutes=60))
def _get_commodities_names_from_spansh() -> list[str]:
    with get_httpx_client() as client:
        res = client.get(SPANSH_COMMODITIES_TYPEAHEAD_SERVICE_URL)
        res.raise_for_status()

    return res.json()["values"]


def _read_commodities_csv_file(path: str, is_rare: bool) -> list[Commodity]:
    """Read a given CSV file and returned the parsed commodities."""
    items: list[Commodity] = []
    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        items.extend(
            Commodity(
                id=int(row["id"]),
                name=row["name"],
                category=row["category"],
                is_rare=is_rare,
            )
            for row in csv_reader
        )
    return items


@cachier(stale_after=datetime.timedelta(days=1))
def _get_commodities() -> list[Commodity]:
    commodities = _read_commodities_csv_file(f"{DATA_PATH}/commodities.csv", False)
    rares = _read_commodities_csv_file(f"{DATA_PATH}/rare_commodities.csv", True)
    return commodities + rares


@cachier(stale_after=datetime.timedelta(days=1))
def _get_commodities_prices_from_inara() -> list[CommodityPrice]:
    prices = []
    commodities = _get_commodities()

    with get_httpx_client() as client:
        inara_res = client.get(INARA_COMMODITIES)
        inara_res.raise_for_status()

        soup = BeautifulSoup(inara_res.text, features="html.parser")

        table_items = (
            entry
            for entry in soup.select("tbody > tr")
            if len(entry.select(".subheader")) == 0
        )

        for entry in table_items:
            columns = [x.text.strip() for x in entry.select("td")]

            commodity = _get_commodity_from_name(columns[0], commodities)
            if commodity is None:
                continue
            prices.append(
                CommodityPrice(
                    commodity=commodity,
                    inara_id=string_to_int(entry.select("a")[0]["href"]),
                    average_buy_price=string_to_int(columns[2]),
                    average_sell_price=string_to_int(columns[1]),
                    minimum_buy_price=string_to_int(columns[5]),
                    maximum_sell_price=string_to_int(columns[4]),
                )
            )

    return prices


class CommoditiesService:
    """Main class for the commodities service."""

    def get_commodities_typeahead(self, input_text: str) -> list[str]:
        """Get commodities names for autocomplete."""
        try:
            commodities = _get_commodities_names_from_spansh()
        except httpx.HTTPError as e:  # type: ignore
            raise ContentFetchingError() from e

        return [
            item for item in commodities if item.lower().startswith(input_text.lower())
        ]

    def get_commodities(self) -> list[Commodity]:
        """Get all commodities."""
        try:
            res = _get_commodities()
        except httpx.HTTPError as e:  # type: ignore
            raise ContentFetchingError() from e
        return res

    def get_commodities_prices(self, filter: str | None) -> list[CommodityPrice]:
        """Get all commodities prices (with an optional filter) ."""
        try:
            res = _get_commodities_prices_from_inara()
        except httpx.HTTPError as e:  # type: ignore
            raise ContentFetchingError() from e
        else:
            if filter:
                return [
                    item
                    for item in res
                    if item.commodity.name.lower().startswith(filter.lower())
                ]
            return res

    def get_commodity_prices(self, commodity_name: str) -> CommodityPrice:
        """Get prices for a specific commodity."""
        try:
            res = _get_commodities_prices_from_inara()
        except httpx.HTTPError as e:  # type: ignore
            raise ContentFetchingError() from e

        matching_commodity = next(
            (
                price
                for price in res
                if price.commodity.name.lower() == commodity_name.lower()
            ),
            None,
        )
        if matching_commodity is None:
            raise CommodityNotFoundError(commodity_name)

        return matching_commodity

    async def find_commodity(
        self,
        mode: FindCommodityMode,
        reference_system: str,
        commodity: str,
        min_landing_pad_size: StationLandingPadSize,
        min_quantity: int,
        max_age_days: int,
    ) -> list[StationWithCommodityDetails]:
        """Get stations buying or selling a specific commodity near a reference system.

        Only works for non-rare commodities.
        Will only include prices from stations where market prices where updates between now
        and now - max_age_days.
        """
        # First get commodity price
        current_commodity_price = self.get_commodity_prices(commodity)

        async with get_async_httpx_client() as client:
            try:
                api_response = await client.post(
                    SPANSH_STATIONS_SEARCH_URL,
                    json=self._find_commodity_generate_request_body(
                        mode, reference_system, commodity, min_quantity, max_age_days
                    ),
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        return self._map_spansh_stations_to_model(
            api_response, current_commodity_price, mode, min_landing_pad_size
        )

    async def get_stations_with_best_prices_for_commodity(
        self, commodity_name: str, max_age_days: int
    ) -> BestPricesStations:
        """Get the best stations to buy and sell a specific commodity.

        Will only include prices from stations where market prices where updates between now
        and now - max_age_days.
        """
        # First get commodity price
        current_commodity_price = self.get_commodity_prices(commodity_name)

        return BestPricesStations(
            best_stations_to_buy=await self._get_station_with_best_prices_for_commodity_and_mode(
                current_commodity_price, max_age_days, FindCommodityMode.BUY
            ),
            best_stations_to_sell=await self._get_station_with_best_prices_for_commodity_and_mode(
                current_commodity_price, max_age_days, FindCommodityMode.SELL
            ),
        )

    async def _get_station_with_best_prices_for_commodity_and_mode(
        self,
        commodity: CommodityPrice,
        max_age_days: int,
        mode: FindCommodityMode,
    ) -> list[StationWithCommodityDetails]:
        """Get the best stations to buy or sell a specific commodity.

        Will only include prices from stations where market prices where updates between now
        and now - max_age_days.
        """
        async with get_async_httpx_client() as client:
            try:
                api_response = await client.post(
                    SPANSH_STATIONS_SEARCH_URL,
                    json=self._find_commodity_best_prices_generate_request_body(
                        mode, commodity.commodity.name, max_age_days
                    ),
                )
                api_response.raise_for_status()
            except httpx.HTTPError as e:  # type: ignore
                raise ContentFetchingError() from e

        return self._map_spansh_stations_to_model(
            api_response, commodity, mode, StationLandingPadSize.SMALL
        )

    def _map_spansh_stations_to_model(
        self,
        api_response: httpx.Response,
        current_commodity_price: CommodityPrice,
        mode: FindCommodityMode,
        min_landing_pad_size: StationLandingPadSize,
    ) -> list[StationWithCommodityDetails]:
        res: list[StationWithCommodityDetails] = []
        for item in api_response.json()["results"]:
            commodity_in_market = next(
                market_item
                for market_item in item["market"]
                if market_item["commodity"] == current_commodity_price.commodity.name
            )
            price = (
                commodity_in_market["buy_price"]
                if mode == FindCommodityMode.BUY
                else commodity_in_market["sell_price"]
            )
            price_percentage_difference = self._get_price_difference(
                current_commodity_price, price, mode
            )
            station_landing_pad_size = get_station_max_landing_pad_size(item)

            if station_landing_pad_size > min_landing_pad_size:
                continue

            res.append(
                StationWithCommodityDetails(
                    distance_from_reference_system=item["distance"],
                    distance_to_arrival=item["distance_to_arrival"],
                    is_planetary=item["is_planetary"],
                    last_market_update=parse(item["market_updated_at"])
                    if item.get("market_updated_at")
                    else None,  # type: ignore
                    max_landing_pad_size=station_landing_pad_size,
                    name=item["name"],
                    price=(
                        commodity_in_market["buy_price"]
                        if mode == FindCommodityMode.BUY
                        else commodity_in_market["sell_price"]
                    ),
                    quantity=(
                        commodity_in_market["supply"]
                        if mode == FindCommodityMode.BUY
                        else commodity_in_market["demand"]
                    ),
                    system_name=item["system_name"],
                    type=item.get("type", "Unknown"),
                    price_percentage_difference=price_percentage_difference,
                    is_fleet_carrier=is_fleet_carrier(
                        item.get("controlling_minor_faction")
                    ),
                    is_settlement=is_settlement(item.get("type")),
                )
            )

        return res

    def _find_commodity_best_prices_generate_request_body(
        self,
        mode: FindCommodityMode,
        commodity: str,
        max_age_days: int,
    ) -> dict:
        body = {
            "filters": {
                "market": [{"name": commodity}],
                "market_updated_at": get_max_age_values_for_request_body(max_age_days),
            },
            "size": 25,
            "page": 0,
        }
        if mode == FindCommodityMode.SELL:
            body["sort"] = [
                {"market_sell_price": [{"name": commodity, "direction": "desc"}]}
            ]
            body["filters"]["market"][0]["demand"] = {  # type: ignore
                "value": [1, 1000000000],
                "comparison": "<=>",
            }
        elif mode == FindCommodityMode.BUY:
            body["sort"] = [
                {"market_buy_price": [{"name": commodity, "direction": "asc"}]}
            ]
            body["filters"]["market"][0]["supply"] = {  # type: ignore
                "value": [1, 1000000000],
                "comparison": "<=>",
            }

        return body

    def _find_commodity_generate_request_body(
        self,
        mode: FindCommodityMode,
        reference_system: str,
        commodity: str,
        min_quantity: int,
        max_age_days: int,
    ) -> dict[str, Any]:
        body = {
            **get_request_body_common_filters(),
            "filters": {
                "market": [
                    {
                        "name": commodity,
                    }
                ],
                "market_updated_at": get_max_age_values_for_request_body(max_age_days),
            },
            "reference_system": reference_system,
        }

        if mode == FindCommodityMode.BUY:
            body["filters"]["market"][0]["supply"] = {  # type: ignore
                "value": [min_quantity, 1000000000],
                "comparison": "<=>",
            }
        else:
            body["filters"]["market"][0]["demand"] = {  # type: ignore
                "value": [min_quantity, 1000000000],
                "comparison": "<=>",
            }

        return body

    def _get_price_difference(
        self,
        commodity_price: CommodityPrice,
        station_price: int,
        mode: FindCommodityMode,
    ) -> int:
        average_price = (
            commodity_price.average_buy_price
            if mode == FindCommodityMode.BUY
            else commodity_price.average_sell_price
        )
        if station_price == 0:
            return 0
        difference = station_price - average_price
        if mode.SELL:
            return round((difference / station_price) * 100.0)
        else:
            return round((difference / average_price) * 100.0)
