# SurrealDB Skill - Run Commands

How to run evaluations and use this skill.

---

## Running Output Quality Evals

This skill uses the skill-evaluator for output quality testing. Run inline:

```bash
# From the skill-evaluator skill directory, or inline in your session
python -m pytest tests/ -k surrealdb
```

Or use the skill-evaluator workflow:

1. Load the surrealdb skill
2. Read `evals/evals.json` to understand test cases
3. For each eval, write the code and verify it meets expectations

---

## Running Triggering Evals

Triggering tests require Claude Code. Use the skill-evaluator:

```bash
# Run trigger evals for surrealdb skill
cd ~/.config/opencode/skills/skill-evaluator
python scripts/run_eval.py --skill surrealdb
```

---

## Testing Locally

### Unit Tests

```bash
# Run ONTO-AEC unit tests related to SurrealDB
cd /Users/marchansen/GitHub/Cover-Architectural/onto-aec
python -m pytest tests/unit/test_db/ -v
```

### Integration Tests

```bash
# Requires SurrealDB running
docker-compose up -d surrealdb

# Run integration tests
python -m pytest tests/integration/ -v
```

---

## Example: Testing a Query

```python
import asyncio
from src.db.surreal_client import get_surreal_client

async def test_query():
    db = await get_surreal_client()
    result = await db.query("SELECT * FROM onto_ontology LIMIT 1")
    print(result)
    await db.close()

asyncio.run(test_query())
```

---

## Dependencies

- Python 3.10+
- surrealdb Python SDK 1.0.8+
- Redis 5.0.1+ (for caching)
- SurrealDB server (for integration tests)

Install dependencies:

```bash
pip install surrealdb redis
```
