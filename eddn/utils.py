#!/usr/bin/env python3

from sqlalchemy import and_

from models.database import Commodity, CommodityPrice, Station, System


def get_price(session, station_id, commodity_name):
    """
    Get the price entry for a commodity at a particular station
    :param session:
    :param station_id:
    :param commodity_name:
    :return:
    """
    cq = session.query(Commodity.id).filter(Commodity.internal_name == commodity_name)
    if cq and cq.count():
        cid = cq.first()[0]

        # get the actual price object for this
        pq = session.query(CommodityPrice).filter(
            and_(
                CommodityPrice.station_id == station_id,
                CommodityPrice.commodity_id == cid
            ))
        if pq and pq.count():
            return pq.first()

    return None


def get_station_by_names(session, star_name, station_name):
    """
    Get the correct station in a system (there are stations and stars with identical names, but not together)
    :param session: session
    :param star_name: name of the star system
    :param station_name: name of the station
    :return:
    """
    stars = session.query(System.id).filter(System.name == star_name)
    if stars and stars.count():
        for star_id in stars.all():
            star_id = star_id[0]
            # find the station
            stations = session.query(Station.id).filter(
                and_(
                    Station.system_id == star_id,
                    Station.name == station_name
                ))
            if stations and stations.count() == 1:
                station = stations.first()[0]
                return session.query(Station).get(station)

    # no match
    return None
