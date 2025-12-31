from typing import List, Optional

from pydantic import BaseModel, Field


class LegalDocument(BaseModel):
    """Model representing a single legal decision record."""

    id: str = Field(..., description="Unique internal ID (e.g., snciv2025333163O)")
    numdec: str = Field(..., description="Decision number as a string")
    filingDate: List[str] = Field(..., alias="datdep")
    presidente: List[str] = Field(default_factory=list)
    relatore: List[str] = Field(default_factory=list)
    type: str = Field(..., alias="tipoprov")
    section: Optional[str] = Field(None, alias="szdec")
    year: Optional[str] = Field(None, alias="anno")
    summary: Optional[List[str]] = Field(None, alias="ocr")
    filename: Optional[List[str]] = Field(None)

    @property
    def cleanPresident(self) -> str:
        """Helper to get the president name without list brackets."""
        return self.presidente[0] if self.presidente else "N/A"
