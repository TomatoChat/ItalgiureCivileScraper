from enum import Enum


class CourtSection(str, Enum):
    """Enumeration of Civil Court Sections (szdec)."""

    SEZIONE_1 = "1"
    SEZIONE_2 = "2"
    SEZIONE_3 = "3"
    SEZIONE_4 = "4"
    SEZIONE_5 = "5"
    SEZIONI_UNITE = "SU"
