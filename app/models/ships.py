from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from aenum import MultiValueEnum
from pydantic.dataclasses import dataclass

from app.models.stations import StationLandingPadSize


class ShipModel(MultiValueEnum):
    ADDER = "Adder", "adder"
    ALLIANCE_CHALLENGER = "Alliance Challenger", "typex_3"
    ALLIANCE_CHIEFTAIN = "Alliance Chieftain", "typex"
    ALLIANCE_CRUSADER = "Alliance Crusader", "typex_2"
    ANACONDA = "Anaconda", "anaconda"
    ASP_EXPLORER = "Asp Explorer", "asp"
    ASP_SCOUT = "Asp Scout", "asp_scout"
    BELUGA_LINER = "Beluga Liner", "belugaliner"
    COBRA_MKIII = "Cobra MkIII", "cobramkiii"
    COBRA_MKIV = "Cobra MkIV", "cobramkiv"
    DIAMONDBACK_EXPLORER = "Diamondback Explorer", "diamondbackxl"
    DIAMONDBACK_SCOUT = "Diamondback Scout", "diamondback"
    DOLPHIN = "Dolphin", "dolphin"
    EAGLE = "Eagle", "eagle"
    FEDERAL_ASSAULT_SHIP = "Federal Assault Ship", "federation_dropship_mkii"
    FEDERAL_CORVETTE = "Federal Corvette", "federation_corvette"
    FEDERAL_DROPSHIP = "Federal Dropship", "federation_dropship"
    FEDERAL_GUNSHIP = "Federal Gunship", "federation_gunship"
    FER_DE_LANCE = "Fer-de-Lance", "ferdelance"
    HAULER = "Hauler", "hauler"
    IMPERIAL_CLIPPER = "Imperial Clipper", "empire_trader"
    IMPERIAL_COURIER = "Imperial Courier", "empire_courier"
    IMPERIAL_CUTTER = "Imperial Cutter", "cutter"
    IMPERIAL_EAGLE = "Imperial Eagle", "empire_eagle"
    KEELBACK = "Keelback", "independant_trader"
    KRAIT_MKII = "Krait MkII", "krait_mkii"
    KRAIT_PHANTOM = "Krait Phantom", "krait_light"
    MAMBA = "Mamba", "mamba"
    ORCA = "Orca", "orca"
    PYTHON = "Python", "python"
    PYTHON_MKII = "Python MkII", "python_nx"
    SIDEWINDER = "Sidewinder", "sidewinder"
    TYPE_10_DEFENDER = "Type-10 Defender", "type9_military"
    TYPE_6_TRANSPORTER = "Type-6 Transporter", "type6"
    TYPE_7_TRANSPORTER = "Type-7 Transporter", "type7"
    TYPE_9_HEAVY = "Type-9 Heavy", "type9"
    VIPER_MKIII = "Viper MkIII", "viper"
    VIPER_MKIV = "Viper MkIV", "viper_mkiv"
    VULTURE = "Vulture", "vulture"

    @staticmethod
    def get_internal_names() -> Iterable[str]:
        """Get a list of ships internal names."""
        return (item.values[1] for item in ShipModel)  # type: ignore

    @staticmethod
    def get_display_names() -> Iterable[str]:
        """Get a list of ships display names."""
        return (item.values[0] for item in ShipModel)  # type: ignore

    @classmethod
    def _missing_(cls: type[ShipModel], value: str) -> ShipModel | None:
        # If missing, check lowercase of any member
        value = value.lower()
        for member in cls:  # type: ignore
            for member_value in member.values:
                if member_value.lower() == value:
                    return member
        return None


@dataclass
class StationSellingShip:
    distance_from_reference_system: float
    distance_to_arrival: float
    is_fleet_carrier: bool
    is_planetary: bool
    is_settlement: bool
    max_landing_pad_size: StationLandingPadSize
    name: str
    shipyard_updated_at: datetime
    system_name: str
