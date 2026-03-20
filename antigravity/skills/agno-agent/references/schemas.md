# agno-Agent Skill References

Reference materials for agno agent development.

---

## Agent Configuration Options

```python
from agno.agent import Agent
from agno.models.mistral import MistralChat
from agno.db.surrealdb import SurrealDb

agent = Agent(
    name="AgentName",
    model=MistralChat(
        id="mistral-small-latest",  # or "mistral-medium-latest"
        temperature=0.0,            # 0.0 for deterministic
        max_tokens=4096,
    ),
    db=SurrealDb(...),             # Memory backend
    description="Agent description",
    instructions=[
        "Instruction 1",
        "Instruction 2",
    ],
    tools=[...],                    # Function tools
    tool_choice="auto",            # or "required", "none"
    markdown=True,                 # Enable markdown in responses
    structured_outputs=True,       # Pydantic model outputs
)
```

---

## Available Agents in ONTO-AEC

| Agent | File | Purpose |
|-------|------|---------|
| DocumentIngestionAgent | `src/agents/ingestion_agent.py` | OCR, section parsing |
| ExtractionAgent | `src/agents/extraction_agent.py` | Concept extraction |
| StructuringAgent | `src/agents/structuring_agent.py` | RDF graph building |
| AlignmentAgent | `src/agents/alignment_agent.py` | Standards alignment |
| ValidationAgent | `src/agents/validation_agent.py` | SHACL validation |
| ExportAgent | `src/agents/export_agent.py` | Multi-format export |

---

## Guardrails

| Guardrail | Purpose |
|-----------|---------|
| IngestionAccuracyGuardrail | Validates OCR quality |
| ExtractionGuardrail | Validates extracted content |
| StructuringGuardrail | Validates RDF structure |
| AlignmentGuardrail | Validates alignment quality |

---

## Dependencies

```bash
pip install agno==2.4.8
```

---

## Tool Function Pattern

```python
from pydantic import BaseModel

class CreateRecordInput(BaseModel):
    table: str
    data: dict

def create_record(input: CreateRecordInput):
    """Create a record in SurrealDB."""
    # Implementation
    return {"id": "...", "created": True}
```
