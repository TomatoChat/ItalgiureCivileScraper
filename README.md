# ItalgiureCivileScraper

A Python tool for scraping legal documents from the Italgiure database and uploading them to HuggingFace datasets.

## Features

- 🔍 **Query Legal Records**: Search and collect legal documents from Italgiure Solr API
- 📄 **PDF Download**: Automatically downloads PDF files from Italgiure
- ☁️ **HuggingFace Integration**: Uploads documents and PDFs to HuggingFace datasets
- 📊 **Progress Tracking**: Real-time progress bars for collection and upload operations
- 🏗️ **Type-Safe Models**: Uses Pydantic for validated data models
- ⚙️ **Configurable**: Settings managed via `.env` file

## Installation

### Prerequisites

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd ItalgiureCivileScraper
```

2. Install dependencies:

```bash
uv sync
# or
pip install -e .
```

3. Create a `.env` file in the root directory:

```bash
cp .env.template .env
```

4. Configure your `.env` file:

```env
HF_TOKEN=your_huggingface_token_here
HF_REPO_ID=username/dataset-name
```

## Configuration

Create a `.env` file in the project root with the following variables:

- `HF_TOKEN`: Your HuggingFace authentication token
- `HF_REPO_ID`: Your HuggingFace repository ID (e.g., `TomatoChat/ItalgiureCivile`)

## Usage

### Basic Usage

Run the main script to collect and upload legal documents:

```bash
python main.py
```

### Programmatic Usage

#### Collect Legal Records

```python
from src.helpers import collectLegalRecords
from src.models import ItalgiureSolrQuery, DatabaseKind

# Collect 10 legal documents
documents = collectLegalRecords(
    ItalgiureSolrQuery(kind=DatabaseKind.CIVILE),
    limit=10,
    downloadPdfs=True  # Download PDFs during collection
)
```

#### Upload to HuggingFace

```python
from src.helpers import uploadToHuggingFace

# Upload documents and PDFs to HuggingFace
fileUrl = uploadToHuggingFace(
    documents=documents,
    repoId="username/dataset-name",
    fileName="data.parquet",
    uploadPdfs=True  # Upload PDFs if they were downloaded
)
```

#### Advanced Query Options

```python
from src.models import ItalgiureSolrQuery, DatabaseKind, CourtSection, SortOrder

# Create a custom query
query = ItalgiureSolrQuery(
    kind=DatabaseKind.CIVILE,
    section=CourtSection.PRIMA_SEZIONE,
    year=2025,
    sortOrder=SortOrder.NEWEST_FIRST,
    rows=50  # Records per page
)

documents = collectLegalRecords(query, limit=100)
```

## Project Structure

```
ItalgiureCivileScraper/
├── main.py                 # Main entry point
├── settings.py             # Application settings
├── pyproject.toml          # Project configuration
├── .env                    # Environment variables (not in git)
├── src/
│   ├── helpers/
│   │   ├── collectLegalRecords.py    # Collect documents from API
│   │   ├── downloadPdfFromItalgiure.py  # Download PDFs
│   │   └── uploadToHuggingFace.py    # Upload to HuggingFace
│   └── models/
│       ├── LegalDocument.py           # Document data model
│       ├── ItalgiureSolrQuery.py      # Query builder
│       ├── DatabaseKind.py            # Database type enum
│       ├── CourtSection.py            # Court section enum
│       └── SortOrder.py               # Sort order enum
└── README.md
```

## Data Model

### LegalDocument

The main data model representing a legal document:

- `id`: Unique internal ID
- `decisionNumber`: Decision number
- `filingDate`: Filing date
- `president`: President name
- `relator`: Relator name
- `type`: Document type
- `section`: Court section
- `year`: Year
- `summary`: OCR summary (optional)
- `italGiureFileName`: Original filename on Italgiure
- `hfFileName`: HuggingFace URL for the PDF
- `originalDecisionCourt`: Original decision court (optional)
- `originalDecisionNumber`: Original decision number (optional)
- `originalDecisionFilingDate`: Original decision filing date (optional)

**Note**: `localPdfPath` is used internally but excluded from the uploaded dataset.

## Workflow

1. **Collection Phase** (`collectLegalRecords`):

   - Queries the Italgiure Solr API
   - Downloads metadata for legal documents
   - Optionally downloads PDFs and stores them locally
   - Returns a list of `LegalDocument` instances

2. **Upload Phase** (`uploadToHuggingFace`):
   - Uploads PDFs to HuggingFace (in `documents/` folder)
   - Updates `hfFileName` with HuggingFace URLs
   - Creates a Parquet file with all document metadata
   - Uploads the Parquet file to HuggingFace

## Output Structure

The HuggingFace repository will contain:

```
repository/
├── data.parquet          # Main dataset file with all metadata
└── documents/            # PDF files
    ├── file1.pdf
    ├── file2.pdf
    └── ...
```

## Development

### Install Development Dependencies

```bash
uv sync --dev
```

### Run Linting

```bash
ruff check .
```

### Type Checking

```bash
ty .
```

## License

See [LICENSE](LICENSE) file for details.
