from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class LegalDocument(BaseModel):
    """Model representing a single legal decision record."""

    id: str = Field(..., description="Unique internal ID (e.g., snciv2025333163O)")
    decisionNumber: str = Field(..., alias="numdec", description="Decision number")
    filingDate: str = Field(..., alias="datdep", description="Filing date")
    president: str = Field(default="", alias="presidente", description="President")
    relator: str = Field(default="", alias="relatore", description="Relator")
    type: str = Field(..., alias="tipoprov", description="Type")
    section: Optional[str] = Field(None, alias="szdec", description="Section")
    year: Optional[str] = Field(None, alias="anno")
    summary: Optional[List[str]] = Field(None, alias="ocr")
    italGiureFileName: Optional[str] = Field(
        None, alias="filename", description="File name on Italgiure"
    )
    hfFileName: str = Field(default="", description="File name on HuggingFace")
    originalDecisionCourt: Optional[str] = Field(
        None, description="Original decision court"
    )
    originalDecisionNumber: Optional[str] = Field(
        None, description="Original decision number"
    )
    originalDecisionFilingDate: Optional[str] = Field(
        None, description="Original decision filing date"
    )

    @field_validator("filingDate", mode="before")
    @classmethod
    def extractFirstFilingDate(cls, v: Union[str, List[str]]) -> str:
        """Extract first item from filingDate list."""
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        elif isinstance(v, str):
            return v
        return ""

    @field_validator("president", mode="before")
    @classmethod
    def extractFirstPresident(cls, v: Union[str, List[str]]) -> str:
        """Extract first item from president list."""
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        elif isinstance(v, str):
            return v
        return ""

    @field_validator("relator", mode="before")
    @classmethod
    def extractFirstRelator(cls, v: Union[str, List[str]]) -> str:
        """Extract first item from relator list."""
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        elif isinstance(v, str):
            return v
        return ""

    @field_validator("italGiureFileName", mode="before")
    @classmethod
    def extractFirstFileName(cls, v: Union[None, str, List[str]]) -> Optional[str]:
        """Extract first item from fileName list."""
        if v is None:
            return None
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        elif isinstance(v, str):
            return v
        return None
