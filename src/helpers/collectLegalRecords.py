import time
from typing import List, Optional

import requests
import urllib3

from src.models import ItalgiureSolrQuery, LegalDocument

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def collectLegalRecords(
    queryObj: ItalgiureSolrQuery,
    limit: Optional[int] = None,
    timeout: int = 15,
    url: str = "https://www.italgiure.giustizia.it/sncass/isapi/hc.dll/sn.solr/sn-collection/select",
    sleep: float = 0.5,
) -> List[LegalDocument]:
    allValidatedDocs: List[LegalDocument] = []
    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.italgiure.giustizia.it/sncass/index.jsp",
        }
    )

    while True:
        if limit and len(allValidatedDocs) >= limit:
            break

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

        if not docsData:
            break

        allValidatedDocs.extend([LegalDocument(**doc) for doc in docsData])

        if queryObj.start + queryObj.rows >= totalFound:
            break

        queryObj.start += queryObj.rows

        time.sleep(sleep)

    return allValidatedDocs[:limit] if limit else allValidatedDocs
