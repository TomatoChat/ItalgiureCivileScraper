from enum import Enum


class SortOrder(str, Enum):
    """Enumeration of valid sorting rules for Italgiure."""

    NEWEST_FIRST = "pd desc,numdec desc"
    OLDEST_FIRST = "pd asc,numdec asc"
    DECISION_NUMBER = "numdec desc"
