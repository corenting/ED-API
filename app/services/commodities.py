import pendulum
from cachier import cachier

from app.helpers.httpx import get_httpx_client
from app.models.commodities import Commodity

TYPEAHEAD_SERVICE_URL = "https://spansh.co.uk/api/stations/field_values/market"
EDDB_COMMODITIES = "https://eddb.io/archive/v6/commodities.json"


@cachier(stale_after=pendulum.duration(minutes=60))
def _get_commodities_names_from_spansh() -> dict:
    # Get API
    with get_httpx_client() as client:
        res = client.get(TYPEAHEAD_SERVICE_URL)

    return res.json()["values"]


@cachier(stale_after=pendulum.duration(days=1))
def _get_commodities_from_eddb() -> list[Commodity]:
    # Get API
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
