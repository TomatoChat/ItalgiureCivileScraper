import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfApi, login
from tqdm import tqdm

from settings import settings
from src.models import LegalDocument


def uploadToHuggingFace(
    documents: list[LegalDocument],
    repoId: str,
    fileName: str = "data.parquet",
    hfToken: str | None = None,
    uploadPdfs: bool = True,
) -> str:
    """
    Uploads a list of LegalDocument instances to a HuggingFace repository as a Parquet file.
    If documents have localPdfPath set, uploads those PDFs to HuggingFace and updates hfFileName.

    Args:
        documents: List of LegalDocument instances to upload (should have localPdfPath if PDFs were downloaded).
        repoId: HuggingFace repository ID (e.g., "username/dataset-name").
        fileName: Name of the file to create/update. Defaults to "data.parquet".
        hfToken: HuggingFace token. If None, reads from settings (HF_TOKEN from .env file).
        uploadPdfs: If True, uploads PDFs that have localPdfPath set. Defaults to True.

    Returns:
        URL of the uploaded file in the HuggingFace repository.

    Raises:
        ValueError: If no token is provided and HF_TOKEN is not found in environment.
        Exception: If upload fails.
    """

    login(token=hfToken or settings.hf_token)

    api = HfApi()
    updatedDocuments = []
    tempFilePath = None
    pdfsToCleanup = []

    try:
        if uploadPdfs:
            documentsWithPdfs = [
                doc
                for doc in documents
                if doc.localPdfPath and Path(doc.localPdfPath).exists()
            ]

            if documentsWithPdfs:
                with tqdm(
                    total=len(documentsWithPdfs),
                    desc="Uploading PDFs to HuggingFace",
                    unit="PDF",
                ) as pbar:
                    for doc in documentsWithPdfs:
                        pdfPath = Path(doc.localPdfPath or "")
                        pdfFileName = pdfPath.name

                        api.upload_file(
                            path_or_fileobj=str(pdfPath),
                            path_in_repo=pdfFileName,
                            repo_id=repoId,
                            repo_type="dataset",
                            commit_message=f"Upload PDF: {pdfFileName}",
                        )

                        hfPdfUrl = f"https://huggingface.co/datasets/{repoId}/resolve/main/{pdfFileName}"
                        doc.hfFileName = hfPdfUrl

                        pdfsToCleanup.append(pdfPath)
                        pbar.update(1)

        updatedDocuments: list[LegalDocument] = documents

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tempFile:
            tempFilePath = Path(tempFile.name)

        pq.write_table(
            pa.Table.from_pylist([doc.model_dump() for doc in updatedDocuments]),
            tempFilePath,
        )

        api.upload_file(
            path_or_fileobj=str(tempFilePath),
            path_in_repo=fileName,
            repo_id=repoId,
            repo_type="dataset",
            commit_message=f"Upload dataset: {len(updatedDocuments)} legal documents to {fileName}",
        )

        return f"https://huggingface.co/datasets/{repoId}/resolve/main/{fileName}"

    finally:
        # Clean up temporary parquet file
        if tempFilePath and tempFilePath.exists():
            tempFilePath.unlink()

        # Clean up downloaded PDFs after upload
        for pdfPath in pdfsToCleanup:
            if pdfPath.exists():
                pdfPath.unlink()

        # Try to clean up the PDF directory if it's empty
        if pdfsToCleanup:
            pdfDir = pdfsToCleanup[0].parent
            try:
                if pdfDir.exists() and not any(pdfDir.iterdir()):
                    pdfDir.rmdir()
            except OSError:
                pass
