SETTLEMENT_TYPE = "Settlement"


def is_settlement(station_type: str | None) -> bool:
    """Check if a station is a settlement according to the type."""
    if station_type is None:
        return False
    return station_type.lower() == SETTLEMENT_TYPE.lower()
