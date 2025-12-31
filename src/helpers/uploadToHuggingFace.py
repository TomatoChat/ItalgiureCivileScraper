import json
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfApi, login

rootDir = Path(__file__).parent.parent.parent

if str(rootDir) not in sys.path:
    sys.path.insert(0, str(rootDir))

from settings import settings  # noqa: E402
from src.models import LegalDocument  # noqa: E402


def uploadToHuggingFace(
    documents: List[LegalDocument],
    repoId: str,
    fileName: str = "data.parquet",
    hfToken: Optional[str] = None,
    commitMessage: Optional[str] = None,
    useJson: bool = False,
) -> str:
    """
    Uploads a list of LegalDocument instances to a HuggingFace repository as a Parquet or JSON file.

    Args:
        documents: List of LegalDocument instances to upload.
        repoId: HuggingFace repository ID (e.g., "username/dataset-name").
        fileName: Name of the file to create/update. Defaults to "data.parquet".
        hfToken: HuggingFace token. If None, reads from settings (HF_TOKEN from .env file).
        commitMessage: Custom commit message. If None, generates a default message.
        useJson: If True, upload as JSON file instead of Parquet. Defaults to False.

    Returns:
        URL of the uploaded file in the HuggingFace repository.

    Raises:
        ValueError: If no token is provided and HF_TOKEN is not found in environment.
        Exception: If upload fails.
    """
    if not documents:
        raise ValueError("documents list cannot be empty")

    login(token=hfToken or settings.hf_token)

    dataDicts = [doc.model_dump() for doc in documents]

    if useJson or fileName.endswith(".json"):
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as tempFile:
            tempFilePath = Path(tempFile.name)

            json.dump(dataDicts, tempFile, ensure_ascii=False, indent=2)
    else:
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tempFile:
            tempFilePath = Path(tempFile.name)

        table = pa.Table.from_pylist(dataDicts)

        pq.write_table(table, tempFilePath)

    try:
        api = HfApi()

        if commitMessage is None:
            commitMessage = f"Upload {len(documents)} legal documents to {fileName}"

        api.upload_file(
            path_or_fileobj=str(tempFilePath),
            path_in_repo=fileName,
            repo_id=repoId,
            repo_type="dataset",
            commit_message=commitMessage,
        )

        fileUrl = f"https://huggingface.co/datasets/{repoId}/resolve/main/{fileName}"

        return fileUrl

    finally:
        if tempFilePath.exists():
            tempFilePath.unlink()
