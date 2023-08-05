FLEET_CARRIER_ECONOMY = "FleetCarrier"


def is_fleet_carrier(station_economy: str | None) -> bool:
    """Check if a station is a fleet carrier according to the economy."""
    if not station_economy:
        return False

    return station_economy.lower() == FLEET_CARRIER_ECONOMY.lower()
