def can_dock_at_station(station_pad, ship_size):
    if station_pad is None:
        return True
    if station_pad == "L":
        return True  # everyone can dock at large pads
    if ship_size == "L":  # can only dock at large pads
        return station_pad == "L"
    return True
