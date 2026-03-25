---
name: mistral-ocr
description: >
  Mistral OCR processing for ONTO-AEC. Provides document OCR using Mistral OCR 3 API,
  cross-page table merging, and provider switching. Use when processing PDF documents,
  extracting text from building codes, or integrating OCR into the ingestion pipeline.
compatibility: >
  Requires Python 3.10+, mistralai SDK, Redis for caching. Inline evaluation works
  in any environment with dependencies installed.
metadata:
  author: ONTO-AEC Team
  version: 1.0.0
  category: ocr
  tags: [ocr, mistral, pdf, document-processing, text-extraction]
  dependencies: [skill-evaluator]
---

# Mistral OCR Skill

Provides OCR processing using Mistral OCR 3 for ONTO-AEC.

## When to Use

- Processing PDF documents for ontology extraction
- Extracting text and tables from building codes
- Cross-page table merging
- Provider switching (Mistral vs PaddleOCR)
- Redis-based OCR caching

**Do not use for**: Image processing, barcode scanning, or non-document OCR.

---

## Core Components

### MistralOCRProvider

```python
from src.tools.ocr import MistralOCRProvider, process_document_ocr

provider = MistralOCRProvider()

# Process a document
result = await provider.process_document(
    file_path="path/to/document.pdf",
    document_id="doc-001"
)
```

### Cross-Page Table Merging

```python
from src.tools.ocr import merge_cross_page_tables
from src.models.ocr_models import PageOCRResult

# Merge tables split across pages
pages = [page1, page2, page3]
merged_pages = merge_cross_page_tables(pages)
```

---

## Common Patterns

### Processing a Document

```python
from src.tools.ocr import process_document_ocr

async def process_building_code(file_path: str, document_id: str):
    """Process a building code PDF with OCR."""
    result = await process_document_ocr(
        file_path=file_path,
        document_id=document_id
    )
    
    # Result is DocumentSectionTree
    for section in result.sections:
        print(f"{section.section_number}: {section.title}")
        print(f"Body length: {len(section.body_text)}")
    
    return result
```

### Extracting Cross-References

```python
from src.tools.ocr import parse_cross_references

def extract_xrefs(section_body: str):
    """Extract cross-references from section body text."""
    xrefs = parse_cross_references(section_body)
    
    for xref in xrefs:
        print(f"{xref['xref_type']}: {xref['target_section_number']}")
    
    return xrefs
```

### Using Redis Cache

```python
from src.tools.redis_tools import cache_ocr_page, get_cached_ocr_page

# Check cache first
cached = await get_cached_ocr_page(document_id, page_hash)
if cached:
    return cached

# Process and cache
result = await provider.process_page(...)
await cache_ocr_page(document_id, page_hash, result)
```

---

## Data Models

### PageOCRResult

```python
from src.models.ocr_models import PageOCRResult

page = PageOCRResult(
    page_num=1,
    markdown="# Section 1.1\n\nContent...",
    tables=[
        TableOCRResult(
            table_id="tbl-0",
            headers=["Column A", "Column B"],
            rows=[["a1", "b1"], ["a2", "b2"]],
            is_complete=True,
        )
    ],
    extraction_status="SUCCESS",
)
```

### DocumentSectionTree

```python
from src.models.entities import DocumentSectionTree

tree = DocumentSectionTree(
    document_id="doc-001",
    document_title="National Building Code 2025",
    sections=[
        DocumentSection(
            section_number="1",
            title="General",
            hierarchy_level="Part",
            body_text="...",
            tables=[...],
        )
    ],
)
```

---

## Provider Switching

ONTO-AEC supports runtime provider switching via Redis:

```python
from src.tools.redis_tools import get_ocr_provider

# Get current provider
provider_name = await get_ocr_provider()
# Returns "mistral" or "paddle"

# Switch provider (via API)
# PUT /api/v1/config/ocr-provider with {"provider": "paddle"}
```

### Available Providers

| Provider | Network | Use Case |
|----------|---------|----------|
| MistralOCRProvider | Yes (cloud) | Default, highest accuracy |
| PaddleOCRProvider | No (local) | Offline, air-gapped |

---

## Cross-Page Table Merge (FR-015)

The system detects tables split across page boundaries and merges them:

```python
# Page 1 ends with incomplete table
# Page 2 starts with continuation
# merge_cross_page_tables() reassembles them

merged = merge_cross_page_tables([page1, page2])

# After merge:
# - Complete table on page 1
# - page2 table marked as merged_from_pages=[1]
# - Column mismatch sets merge_failed=True
```

---

## Error Handling

```python
from src.tools.ocr import OCRProviderError

try:
    result = await provider.process_document(file_path)
except OCRProviderError as e:
    logger.error(f"OCR failed: {e}")
    # Handle error - retry, fallback, etc.
```

---

## Examples

See `examples/` directory:

- `examples/process_document.py` - Basic document processing
- `examples/extract_tables.py` - Table extraction
- `examples/xref_extraction.py` - Cross-reference parsing
- `examples/provider_switching.py` - Runtime provider changes
