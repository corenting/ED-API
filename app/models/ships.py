from enum import Enum

SHIP_NAMES = [
    "Adder",
    "Alliance Challenger",
    "Alliance Chieftain",
    "Alliance Crusader",
    "Anaconda",
    "Asp Explorer",
    "Asp Scout",
    "Beluga",
    "Cobra Mk. III",
    "Cobra Mk. IV",
    "Diamondback Explorer",
    "Diamondback Scout",
    "Dolphin",
    "Eagle",
    "Federal Assault Ship",
    "Federal Corvette",
    "Federal Dropship",
    "Federal Gunship",
    "Fer-de-Lance",
    "Hauler",
    "Imperial Clipper",
    "Imperial Courier",
    "Imperial Cutter",
    "Imperial Eagle",
    "Keelback",
    "Krait Mk. II",
    "Krait Phantom",
    "Mamba",
    "Orca",
    "Python",
    "Sidewinder",
    "Type-10 Defender",
    "Type-6 Transporter",
    "Type-7 Transporter",
    "Type-9 Heavy",
    "Viper Mk. III",
    "Viper Mk. IV",
    "Vulture",
]


class ShipModel(Enum):
    ADDER = "adder"
    ANACONDA = "anaconda"
    ASP = "asp"
    ASP_SCOUT = "asp_scout"
    BELUGALINER = "belugaliner"
    COBRAMKIII = "cobramkiii"
    COBRAMKIV = "cobramkiv"
    CUTTER = "cutter"
    DIAMONDBACK = "diamondback"
    DIAMONDBACKXL = "diamondbackxl"
    DOLPHIN = "dolphin"
    EAGLE = "eagle"
    EMPIRE_COURIER = "empire_courier"
    EMPIRE_EAGLE = "empire_eagle"
    EMPIRE_TRADER = "empire_trader"
    FEDDROPSHIP = "federation_dropship"
    FEDDROPSHIP_MKII = "federation_dropship_mkii"
    FEDERATION_CORVETTE = "federation_corvette"
    FEDERATION_GUNSHIP = "federation_gunship"
    FERDELANCE = "ferdelance"
    HAULER = "hauler"
    INDEPENDANT_TRADER = "independant_trader"
    KRAIT_LIGHT = "krait_light"
    KRAIT_MKII = "krait_mkii"
    MAMBA = "mamba"
    ORCA = "orca"
    PYTHON = "python"
    SIDEWINDER = "sidewinder"
    TYPE6 = "type6"
    TYPE7 = "type7"
    TYPE9 = "type9"
    TYPE9_MILITARY = "type9_military"
    TYPEX = "typex"
    TYPEX_2 = "typex_2"
    TYPEX_3 = "typex_3"
    VIPER = "viper"
    VIPER_MKIV = "viper_mkiv"
    VULTURE = "vulture"
