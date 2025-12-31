from enum import Enum


class DatabaseKind(str, Enum):
    """Enumeration for the target database."""

    CIVILE = "snciv"
    PENALE = "snpen"
