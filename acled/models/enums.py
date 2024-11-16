from enum import Enum


class TimePrecision(Enum):
    EXACT_DATE = 1
    APPROXIMATE_DATE = 2
    ESTIMATED_DATE = 3


class DisorderType(Enum):
    POLITICAL_VIOLENCE = "Political violence"
    DEMONSTRATIONS = "Demonstrations"
    STRATEGIC_DEVELOPMENTS = "Strategic developments"


class ExportType(Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    XLSX = "xlsx"
    TXT = "txt"

class Actor(Enum):
    """
    Can be used for inter1 and inter2 values
    """
    STATE_FORCES = 1
    REBEL_FORCES = 2
    MILITIA_GROUPS = 3
    COMMUNAL_IDENTITY_GROUPS = 4
    RIOTERS = 5
    PROTESTERS = 6
    CIVILIANS = 7
    FOREIGN_OTHERS = 8

class Region(Enum):
    WESTERN_AFRICA = 1
    MIDDLE_AFRICA = 2
    EASTERN_AFRICA = 3
    SOUTHERN_AFRICA = 4
    NOTHERN_AFRICA = 5
    _ = 6 # missing from documentation
    SOUTH_ASIA = 7
    __ = 8 # also missing from documentation
    SOUTHEAST_ASIA = 9
    ___ = 10 # also missing from documentation
    MIDDLE_EAST = 11
    EUROPE = 12
    CAUCASUS_AND_CENTRAL_ASIA = 13
    CENTRAL_AMERICA = 14
    SOUTH_AMERICA = 15
    CARIBBEAN = 16
    EAST_ASIA = 17
    NORTH_AMERICA = 18
    OCEANIA = 19
    ANTARCTICA = 20
