import difflib

import pendulum
from bs4 import BeautifulSoup
from cachier import cachier

from app.helpers.httpx import get_httpx_client
from app.helpers.string import string_to_int
from app.models.commodities import Commodity, CommodityPrice

TYPEAHEAD_SERVICE_URL = "https://spansh.co.uk/api/stations/field_values/market"
EDDB_COMMODITIES = "https://eddb.io/archive/v6/commodities.json"
INARA_COMMODITIES = "https://inara.cz/commodities/"


def _get_commodity_from_name(name: str, commodities: list[Commodity]) -> Commodity:
    """Get the commodity with the specified name using difflib for handling small differences."""
    valid_name = difflib.get_close_matches(name, [x.name for x in commodities])[0]

    return next(x for x in commodities if x.name == valid_name)


@cachier(stale_after=pendulum.duration(minutes=60))
def _get_commodities_names_from_spansh() -> dict:
    with get_httpx_client() as client:
        res = client.get(TYPEAHEAD_SERVICE_URL)

    return res.json()["values"]


@cachier(stale_after=pendulum.duration(days=1))
def _get_commodities_from_eddb() -> list[Commodity]:
    with get_httpx_client() as client:
        res = client.get(EDDB_COMMODITIES)

    json_content = res.json()

    return [
        Commodity(
            id=item["id"],
            name=item["name"],
            category=item["category"]["name"],
            is_rare=bool(item["is_rare"]),
        )
        for item in json_content
    ]


@cachier(stale_after=pendulum.duration(days=1))
def _get_commodities_prices_from_inara() -> list[CommodityPrice]:
    prices = []
    commodities = _get_commodities_from_eddb()

    with get_httpx_client() as client:
        inara_res = client.get(INARA_COMMODITIES)
        soup = BeautifulSoup(inara_res.text, features="html.parser")

        table_items = (
            entry
            for entry in soup.select("tbody > tr")
            if len(entry.select(".subheader")) == 0
        )

        for entry in table_items:
            columns = [x.text.strip() for x in entry.select("td")]
            prices.append(
                CommodityPrice(
                    commodity=_get_commodity_from_name(columns[0], commodities),
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
        commodities = _get_commodities_names_from_spansh()
        return [
            item for item in commodities if item.lower().startswith(input_text.lower())
        ]

    def get_commodities(self) -> list[Commodity]:
        """Get all commodities."""
        return _get_commodities_from_eddb()

    def get_commodities_prices(self) -> list[CommodityPrice]:
        """Get all commodities prices."""
        return _get_commodities_prices_from_inara()
