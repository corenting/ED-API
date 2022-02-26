from typing import Iterable, Optional

from aenum import MultiValueEnum
from pendulum.datetime import DateTime
from pydantic.dataclasses import dataclass

from app.models.stations import StationLandingPadSize


class ShipModel(MultiValueEnum):
    ADDER = "Adder", "adder"
    ANACONDA = "Alliance Challenger", "anaconda"
    ASP = "Alliance Chieftain", "asp"
    ASP_SCOUT = "Alliance Crusader", "asp_scout"
    BELUGALINER = "Anaconda", "belugaliner"
    COBRAMKIII = "Asp Explorer", "cobramkiii"
    COBRAMKIV = "Asp Scout", "cobramkiv"
    CUTTER = "Beluga", "cutter"
    DIAMONDBACK = "Cobra Mk. III", "diamondback"
    DIAMONDBACKXL = "Cobra Mk. IV", "diamondbackxl"
    DOLPHIN = "Diamondback Explorer", "dolphin"
    EAGLE = "Diamondback Scout", "eagle"
    EMPIRE_COURIER = "Dolphin", "empire_courier"
    EMPIRE_EAGLE = "Eagle", "empire_eagle"
    EMPIRE_TRADER = "Federal Assault Ship", "empire_trader"
    FEDDROPSHIP = "Federal Corvette", "federation_dropship"
    FEDDROPSHIP_MKII = "Federal Dropship", "federation_dropship_mkii"
    FEDERATION_CORVETTE = "Federal Gunship", "federation_corvette"
    FEDERATION_GUNSHIP = "Fer-de-Lance", "federation_gunship"
    FERDELANCE = "Hauler", "ferdelance"
    HAULER = "Imperial Clipper", "hauler"
    INDEPENDANT_TRADER = "Imperial Courier", "independant_trader"
    KRAIT_LIGHT = "Imperial Cutter", "krait_light"
    KRAIT_MKII = "Imperial Eagle", "krait_mkii"
    MAMBA = "Keelback", "mamba"
    ORCA = "Krait Mk. II", "orca"
    PYTHON = "Krait Phantom", "python"
    SIDEWINDER = "Mamba", "sidewinder"
    TYPE6 = "Orca", "type6"
    TYPE7 = "Python", "type7"
    TYPE9 = "Sidewinder", "type9"
    TYPE9_MILITARY = "Type-10 Defender", "type9_military"
    TYPEX = "Type-6 Transporter", "typex"
    TYPEX_2 = "Type-7 Transporter", "typex_2"
    TYPEX_3 = "Type-9 Heavy", "typex_3"
    VIPER = "Viper Mk. III", "viper"
    VIPER_MKIV = "Viper Mk. IV", "viper_mkiv"
    VULTURE = "Vulture", "vulture"

    @staticmethod
    def get_internal_names() -> Iterable[str]:
        """Get a list of ships internal names."""
        return (item.values[1] for item in ShipModel)  # type: ignore

    @staticmethod
    def get_display_names() -> Iterable[str]:
        """Get a list of ships display names."""
        return (item.values[0] for item in ShipModel)  # type: ignore


@dataclass
class StationSellingShip:
    distance_from_reference_system: float
    distance_to_arrival: float
    is_fleet_carrier: bool
    is_planetary: bool
    is_settlement: bool
    max_landing_pad_size: Optional[StationLandingPadSize]
    name: str
    shipyard_updated_at: DateTime
    system_name: str
