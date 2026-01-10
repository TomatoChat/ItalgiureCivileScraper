import tempfile
import time
from pathlib import Path

import requests
import urllib3
from tqdm import tqdm

from src.models import ItalgiureSolrQuery, LegalDocument

from .downloadPdfFromItalgiure import downloadPdfFromItalgiure

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def collectLegalRecords(
    queryObj: ItalgiureSolrQuery,
    limit: int | None = None,
    timeout: int = 15,
    url: str = "https://www.italgiure.giustizia.it/sncass/isapi/hc.dll/sn.solr/sn-collection/select",
    sleep: float = 0.5,
    downloadPdfs: bool = True,
    pdfTimeout: int = 30,
) -> list[LegalDocument]:
    allValidatedDocs: list[LegalDocument] = []
    session = requests.Session()
    tempPdfDir = None

    if downloadPdfs:
        tempPdfDir = Path(tempfile.mkdtemp())

    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.italgiure.giustizia.it/sncass/index.jsp",
        }
    )

    progressBar = None

    while True:
        if limit and len(allValidatedDocs) >= limit:
            break

        try:
            response = session.get(
                url=url,
                params=queryObj.toParams(),
                verify=False,
                timeout=timeout,
            )
            response.raise_for_status()
            rawPayload = response.json()

            totalFound = rawPayload.get("response", {}).get("numFound", 0)
            docsData = rawPayload.get("response", {}).get("docs", [])

            if progressBar is None:
                totalForProgress = limit if limit else totalFound
                progressBar = tqdm(
                    total=totalForProgress,
                    desc="Collecting legal records",
                    unit="documents",
                )

            if not docsData:
                break

            newDocs = [LegalDocument(**doc) for doc in docsData]

            if downloadPdfs and tempPdfDir:
                kind = queryObj.kind.value
                docsWithPdfs = [doc for doc in newDocs if doc.italGiureFileName]

                if docsWithPdfs:
                    pdfProgressBar = tqdm(
                        total=len(docsWithPdfs),
                        desc="Downloading PDFs",
                        unit="PDF",
                        leave=False,
                    )

                    for doc in docsWithPdfs:
                        pdfPath = downloadPdfFromItalgiure(
                            doc.italGiureFileName,
                            kind=kind,
                            timeout=pdfTimeout,
                            tempDir=tempPdfDir,
                        )
                        if pdfPath:
                            doc.localPdfPath = str(pdfPath)

                        pdfProgressBar.update(1)
                    pdfProgressBar.close()

            allValidatedDocs.extend(newDocs)
            progressBar.update(len(newDocs))

            if queryObj.start + queryObj.rows >= totalFound:
                break

            queryObj.start += queryObj.rows
            time.sleep(sleep)

        except Exception as e:
            print(f"❌ Critical error in collection loop: {e}")
            break

    if progressBar:
        progressBar.close()

    return allValidatedDocs[:limit] if limit else allValidatedDocs
