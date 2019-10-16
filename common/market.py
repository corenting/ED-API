def price_difference(average_price, station_price, is_selling):
    if station_price == 0:
        return 0
    difference = station_price - average_price
    if is_selling:
        return round((difference / station_price) * 100.0)
    else:
        return round((difference / average_price) * 100.0)
