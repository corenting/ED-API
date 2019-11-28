import json
import tempfile

import requests
from jsonlines import jsonlines

from api.helpers.request import get_requests_headers
from common.utils import timestamp_to_date
from models.database import (
    StationModuleLink,
    StationShipLink,
    Station,
    Ship,
    System,
    Module,
    ModuleGroup,
)
from models.internal.import_exception import ImportException


def remove_existing_data(db_session):
    db_session.query(StationModuleLink).delete()
    db_session.query(Module).delete()
    db_session.query(ModuleGroup).delete()
    db_session.query(StationShipLink).delete()
    db_session.query(Station).delete()
    db_session.query(Ship).delete()
    db_session.query(System).delete()


def import_ships(ships_file, db_session):
    """
    Import all the ships objects
    :param ships_file: the jsonl dump to import
    :param db_session: SQLAlchemy database session
    """
    ships_list = []
    with jsonlines.Reader(ships_file) as reader:
        print("    Ships import started")
        for s in reader:
            for sh in s["selling_ships"]:
                ship = Ship(name=sh)
                if not any(db_ship.name == ship.name for db_ship in ships_list):
                    ships_list.append(ship)
            for ship_elt in ships_list:
                db_session.add(ship_elt)
    db_session.flush()
    print("    Ships import finished")
    return ships_list


def import_modules(db_session):
    print("    Modules import started")

    # Download JSON
    req = requests.get(
        "https://eddb.io/archive/v6/modules.json", headers=get_requests_headers()
    )

    if req.status_code != 200:
        raise ImportException(
            "Error " + str(req.status_code) + " while downloading modules.json"
        )

    body = req.content
    eddb_json = json.loads(body.decode("utf-8"))
    req.close()

    # First loop to add modules groups
    modules_groups = []
    for module in eddb_json:
        group = ModuleGroup(
            id=module["group"]["id"],
            category_id=module["group"]["category_id"],
            name=module["group"]["name"],
            category=module["group"]["category"],
        )
        if not any(db_module.id == group.id for db_module in modules_groups):
            modules_groups.append(group)
    db_session.bulk_save_objects(modules_groups)
    db_session.flush()

    # Second loop to add the modules themselves
    modules_to_add = []
    for module in eddb_json:
        modules_to_add.append(
            Module(
                id=module["id"],
                module_class=module["class"],
                rating=module["rating"],
                price=module["price"],
                group_id=module["group_id"],
            )
        )
    db_session.bulk_save_objects(modules_to_add)
    db_session.flush()
    print("    Modules import finished")


def import_systems(db_session):
    """
    Import all the systems objects
    :param db_session: SQLAlchemy database session
    """
    # Download systems JSONL
    with tempfile.TemporaryFile() as file:
        req = requests.get(
            "https://eddb.io/archive/v6/systems_populated.jsonl",
            headers=get_requests_headers(),
        )

        # Check errors
        if req.status_code != 200:
            raise ImportException(
                "Error "
                + str(req.status_code)
                + " while downloading systems_populated.jsonl"
            )

        file.write(req.content)
        req.close()
        file.seek(0)

        # First loop to add systems
        with jsonlines.Reader(file) as reader:
            # Add system
            for s in reader:
                system = System(
                    id=s["id"],
                    x=s["x"],
                    y=s["y"],
                    z=s["z"],
                    name=s["name"],
                    permit_required=s["needs_permit"],
                    allegiance=s["allegiance"],
                    government=s["government"],
                    security=s["security"],
                    primary_economy=s["primary_economy"],
                    updated_at=s["updated_at"],
                    population=s["population"],
                    power=s["power"],
                    power_state=s["power_state"],
                )
                db_session.add(system)
    db_session.flush()
    print("Systems import finished")


def import_systems_and_stations(db_session):
    """
    Main function, calling other functions and importing
    stations and related objects
    :param db_session: SQLAlchemy database session
    :return: boolean if successful or not
    """
    try:
        print("Systems/stations import started")
        remove_existing_data(db_session)

        import_modules(db_session)
        import_systems(db_session)

        print("Stations import started")
        with tempfile.TemporaryFile() as file:
            req = requests.get(
                "https://eddb.io/archive/v6/stations.jsonl",
                headers=get_requests_headers(),
            )

            # Check errors
            if req.status_code != 200:
                raise ImportException(
                    "Error "
                    + str(req.status_code)
                    + " while downloading stations.jsonl"
                )

            file.write(req.content)
            req.close()
            file.seek(0)

            # First loop to add ships
            ships_added = import_ships(file, db_session)

            # Second loop to add the stations themselves and the association tables
            file.seek(0)
            with jsonlines.Reader(file) as reader:
                for item in reader:
                    last_shipyard_update = timestamp_to_date(
                        item["shipyard_updated_at"]
                    )

                    landing_pad_size = item["max_landing_pad_size"]
                    if landing_pad_size == "None":
                        landing_pad_size = None

                    new_station = Station(
                        name=item["name"],
                        id=item["id"],
                        is_planetary=item["is_planetary"],
                        max_landing_pad=landing_pad_size,
                        distance_to_star=item["distance_to_star"],
                        type=item["type"],
                        system_id=item["system_id"],
                        last_shipyard_update=last_shipyard_update,
                    )
                    db_session.add(new_station)
                    db_session.flush()

                    # Ships sold by the station
                    ships_array = item["selling_ships"]
                    ships_to_add = []
                    if len(ships_array) != 0:
                        for ship in ships_array:
                            db_ship = next(
                                (x for x in ships_added if x.name == ship), None
                            )
                            ships_to_add.append(
                                StationShipLink(
                                    station_id=new_station.id, ship_id=db_ship.id
                                )
                            )
                    db_session.bulk_save_objects(ships_to_add)

                    # Modules sold by the station
                    modules_array = item["selling_modules"]
                    modules_to_add = []
                    if len(modules_array) != 0:
                        for module in modules_array:
                            modules_to_add.append(StationModuleLink(
                                station_id=new_station.id,
                                module_id=module
                            ))
                    db_session.bulk_save_objects(modules_to_add)

        db_session.commit()
        print("Systems/stations import finished")

        return True
    except Exception as e:
        print("Systems/stations import error (" + str(e) + ")")
        db_session.rollback()
        return False
