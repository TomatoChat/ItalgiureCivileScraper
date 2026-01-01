import logging

from settings import settings
from src.helpers import collectLegalRecords, uploadToHuggingFace
from src.models import DatabaseKind, ItalgiureSolrQuery

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def main():
    """Collect legal records and upload them to HuggingFace."""
    documents = collectLegalRecords(
        ItalgiureSolrQuery(kind=DatabaseKind.CIVILE), limit=10
    )

    fileUrl = uploadToHuggingFace(
        documents=documents,
        repoId=settings.hf_repo_id,
        fileName="data.csv",
        hfToken=settings.hf_token,
    )

    logger.info(f"Successfully uploaded to: {fileUrl}")


if __name__ == "__main__":
    main()
