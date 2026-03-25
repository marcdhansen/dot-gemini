# agno-Agent Skill - Run Commands

How to run evaluations and use this skill.

---

## Running Output Quality Evals

Use the skill-evaluator workflow:

1. Load the agno-agent skill
2. Read `evals/evals.json` to understand test cases
3. For each eval, write the code and verify it meets expectations

---

## Running Triggering Evals

Triggering tests require Claude Code:

```bash
cd ~/.config/opencode/skills/skill-evaluator
python scripts/run_eval.py --skill agno-agent
```

---

## Testing Locally

### Unit Tests

```bash
cd /Users/marchansen/GitHub/Cover-Architectural/onto-aec
python -m pytest tests/unit/test_agents/ -v
```

---

## Dependencies

```bash
pip install agno==2.4.8
```

---

## Example: Creating an Agent

```python
from agno.agent import Agent
from agno.db.surrealdb import SurrealDb
from agno.models.mistral import MistralChat

def create_extraction_agent():
    db = SurrealDb(
        db_url="ws://localhost:8000/rpc",
        db_creds={"username": "root", "password": "root"},
        db_ns="aec",
        db_db="agent_memory",
    )
    
    return Agent(
        name="ExtractionAgent",
        model=MistralChat(id="mistral-small-latest", temperature=0.0),
        db=db,
        description="Extracts ontology concepts from AEC documents",
        instructions=[
            "Extract all named concepts from the document",
            "Identify relationships between concepts",
            "Preserve source section references",
        ],
    )
```
