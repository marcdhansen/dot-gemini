# Mistral OCR Skill References

Reference materials for Mistral OCR processing.

---

## Data Models

### PageOCRResult

```python
from src.models.ocr_models import PageOCRResult

page = PageOCRResult(
    page_num=1,
    markdown="# 1.1 General\n\nContent...",
    tables=[
        TableOCRResult(
            table_id="tbl-0",
            headers=["Col A", "Col B"],
            rows=[["a1", "b1"], ["a2", "b2"]],
            is_complete=True,
            merged_from_pages=[],
        )
    ],
    extraction_status="SUCCESS",  # or "FAILED", "PARTIAL"
    page_hash="abc123",
)
```

### DocumentSection

```python
from src.models.entities import DocumentSection

section = DocumentSection(
    section_number="1.1",
    title="General",
    hierarchy_level="Section",  # Part, Division, Article, Section
    body_text="Full section text...",
    tables=[...],
    figures=[...],
    cross_references=[...],
)
```

---

## Cross-Reference Patterns

```python
# NBC/BCBC patterns
XREF_PATTERNS = [
    ("sentence", r"Sentence (\d+(?:\.\d+)+\(\d+\))"),
    ("table", r"Table (\d+(?:\.\d+)+)"),
    ("article", r"Article (\d+(?:\.\d+)+)"),
    ("clause", r"Clause (\d+(?:\.\d+)+)"),
    ("section", r"Section (\d+(?:\.\d+)*)"),
]
```

---

## Cache Keys

```python
# Redis cache key pattern
CACHE_KEY = "onto:ocr:{document_id}:{page_hash}"
TTL = 86400  # 24 hours
```

---

## Dependencies

```bash
pip install mistralai
pip install pypdf  # For PDF metadata
pip install lxml   # For HTML/XML parsing
```
