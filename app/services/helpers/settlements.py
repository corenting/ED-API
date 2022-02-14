SETTLEMENT_TYPE = "Settlement"


def is_settlement(station_type: str) -> bool:
    """Check if a station is a settlement according to the type."""
    return station_type.lower() == SETTLEMENT_TYPE.lower()
