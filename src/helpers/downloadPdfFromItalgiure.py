import logging
import tempfile
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


def downloadPdfFromItalgiure(
    italGiureFileName: str,
    kind: str = "snciv",
    timeout: int = 30,
    tempDir: Path | None = None,
) -> Path | None:
    """
    Downloads a PDF from the Italgiure 'clean' application path with error handling.
    """
    cleanFileName = italGiureFileName.lstrip("./")
    cleanId = cleanFileName

    if not cleanId.endswith(".clean.pdf"):
        cleanId = cleanId.replace(".pdf", ".clean.pdf")

    pdfUrl = (
        "https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll"
        f"?verbo=attach&db={kind}&id={cleanId}"
    )

    if tempDir is None:
        tempDir = Path(tempfile.gettempdir())
    else:
        tempDir.mkdir(parents=True, exist_ok=True)

    actualFileName = Path(cleanId).name
    pdfPath = tempDir / actualFileName
    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.italgiure.giustizia.it/sncass/index.jsp",
        }
    )

    try:
        response = session.get(pdfUrl, verify=False, timeout=timeout, stream=True)

        response.raise_for_status()

        with open(pdfPath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return pdfPath

    except requests.exceptions.RequestException as e:
        logger.warning(f"Skipping PDF: {actualFileName} | Reason: {e}")
        return None
