# Mistral OCR Skill - Run Commands

How to run evaluations and use this skill.

---

## Running Output Quality Evals

Use the skill-evaluator workflow:

1. Load the mistral-ocr skill
2. Read `evals/evals.json` to understand test cases
3. For each eval, write the code and verify it meets expectations

---

## Running Triggering Evals

Triggering tests require Claude Code:

```bash
cd ~/.config/opencode/skills/skill-evaluator
python scripts/run_eval.py --skill mistral-ocr
```

---

## Testing Locally

### Unit Tests

```bash
cd /Users/marchansen/GitHub/Cover-Architectural/onto-aec
python -m pytest tests/unit/test_ocr_models.py -v
python -m pytest tests/unit/test_table_merge.py -v
```

---

## Dependencies

```bash
pip install mistralai pypdf lxml redis
```

---

## Example: Processing a Document

```python
import asyncio
from src.tools.ocr import process_document_ocr

async def main():
    result = await process_document_ocr(
        file_path="docs/nbc-2025.pdf",
        document_id="nbc-2025-en"
    )
    
    for section in result.sections:
        print(f"{section.section_number}: {section.title}")

asyncio.run(main())
```
