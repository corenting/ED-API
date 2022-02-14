FLEET_CARRIER_ECONOMY = "FleetCarrier"


def is_fleet_carrier(station_economy: str) -> bool:
    """Check if a station is a fleet carrier according to the economy."""
    return station_economy.lower() == FLEET_CARRIER_ECONOMY.lower()
