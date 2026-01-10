from pydantic import BaseModel, Field

from .CourtSection import CourtSection
from .DatabaseKind import DatabaseKind
from .SortOrder import SortOrder


class ItalgiureSolrQuery(BaseModel):
    """Validated model for Italgiure Solr API parameters."""

    kind: DatabaseKind = Field(default=DatabaseKind.CIVILE, alias="kind")
    section: CourtSection | None = Field(default=None, alias="szdec")
    year: int | None = Field(default=None, alias="anno")
    sortOrder: SortOrder = Field(default=SortOrder.NEWEST_FIRST, alias="sort")
    start: int = Field(default=0, ge=0)
    rows: int = Field(default=10, le=500)
    format: str = Field(default="json", alias="wt")
    fields: str = Field(
        default="id,numdec,presidente,datdep,tipoprov,filename", alias="fl"
    )

    def toLuceneQuery(self) -> str:
        """Constructs the dynamic Lucene 'q' string."""
        clauses = [f'kind:"{self.kind.value}"']

        if self.section:
            clauses.append(f'szdec:"{self.section.value}"')

        if self.year:
            clauses.append(f'anno:"{self.year}"')

        return " AND ".join(clauses)

    def toParams(self) -> dict:
        """Generates the parameter dictionary for requests."""
        return {
            "q": self.toLuceneQuery(),
            "app.query": self.kind.value,
            "wt": self.format,
            "start": self.start,
            "rows": self.rows,
            "sort": self.sortOrder.value,
            "fl": self.fields,
        }
