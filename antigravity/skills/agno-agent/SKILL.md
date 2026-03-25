---
name: agno-agent
description: >
  agno agent framework for ONTO-AEC. Provides patterns for building multi-agent pipelines
  with orchestration, memory management, and guardrail integration. Use when creating
  new agents, designing agent workflows, or integrating with the existing pipeline.
compatibility: >
  Requires Python 3.10+, agno-agi 2.4.8+, SurrealDB for memory, Redis for caching.
metadata:
  author: ONTO-AEC Team
  version: 1.0.0
  category: agent-framework
  tags: [agno, agent, pipeline, orchestration, memory, guardrails]
  dependencies: [skill-evaluator, surrealdb]
---

# agno Agent Framework Skill

Provides patterns for building agents with the agno framework in ONTO-AEC.

## When to Use

- Creating new agents for the ONTO-AEC pipeline
- Designing multi-agent orchestration workflows
- Configuring agent memory with SurrealDB
- Integrating guardrails into agent pipelines
- Setting up tools and function calling

**Do not use for**: General Python programming, non-agent workflows, or other agent frameworks.

---

## ONTO-AEC Agent Pipeline

The platform uses a 6-agent pipeline:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Orchestrator│───▶│ Ingestion   │───▶│ Extraction  │
└─────────────┘    └─────────────┘    └─────────────┘
                          │                   │
                          ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  Structuring│───▶│  Alignment  │
                   └─────────────┘    └─────────────┘
                          │                   │
                          ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  Validation │    │   Export    │
                   └─────────────┘    └─────────────┘
```

| Agent | Purpose |
|-------|---------|
| Orchestrator | Coordinates pipeline, manages state |
| Ingestion | OCR processing, section parsing |
| Extraction | Content extraction, concept identification |
| Structuring | RDF graph building, property creation |
| Alignment | Standards alignment (IFC, OmniClass) |
| Validation | SHACL validation, rule enforcement |
| Export | Multi-format serialization |

---

## Agent Pattern

```python
from agno.agent import Agent
from agno.db.surrealdb import SurrealDb
from agno.models.mistral import MistralChat

def _build_agent() -> Agent:
    """Construct an agno Agent instance."""
    
    # Configure SurrealDB memory
    surreal_db = SurrealDb(
        db_url="ws://localhost:8000/rpc",
        db_creds={"username": "root", "password": "root"},
        db_ns="aec",
        db_db="agent_memory",
    )
    
    return Agent(
        name="AgentName",
        model=MistralChat(id="mistral-small-latest", temperature=0.0),
        db=surreal_db,
        description="Agent description for the model",
        instructions=[
            "Instruction 1",
            "Instruction 2",
        ],
        tools=[...],
    )
```

---

## Agent Components

### Model Configuration

```python
from agno.models.mistral import MistralChat
from agno.models.openai import OpenAIChat

# Mistral (ONTO-AEC default)
model = MistralChat(id="mistral-small-latest", temperature=0.0)

# Or OpenAI
model = OpenAIChat(id="gpt-4o", temperature=0.0)
```

### Memory (SurrealDB)

```python
from agno.db.surrealdb import SurrealDb

db = SurrealDb(
    db_url="ws://localhost:8000/rpc",
    db_creds={"username": "root", "password": "root"},
    db_ns="aec",
    db_db="agent_memory",
)
```

### Tools

```python
from src.tools.surreal_tools import create_record, update_record

agent = Agent(
    tools=[create_record, update_record],  # Add functions as tools
)
```

### Guardrails

```python
from src.guardrails.ingestion_guardrail import IngestionAccuracyGuardrail

# Guardrails run after agent execution
# They validate outputs and can raise exceptions
```

---

## Pipeline Orchestration

```python
class OntologyPipeline:
    """Orchestrates the full agent pipeline."""
    
    def __init__(self):
        self.ingestion = DocumentIngestionAgent()
        self.extraction = ExtractionAgent()
        self.structuring = StructuringAgent()
        self.alignment = AlignmentAgent()
        self.validation = ValidationAgent()
        self.export = ExportAgent()
    
    async def process(self, document_id: str):
        # Ingestion → Extraction → Structuring → Alignment → Validation → Export
        result = await self.ingestion.process(document_id)
        result = await self.extraction.process(result)
        result = await self.structuring.process(result)
        result = await self.alignment.process(result)
        result = await self.validation.process(result)
        return await self.export.process(result)
```

---

## Environment Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SURREALDB_URL` | `ws://localhost:8000/rpc` | WebSocket URL |
| `SURREALDB_USER` | `root` | Username |
| `SURREALDB_PASS` | `root` | Password |
| `OPENAI_API_KEY` | - | For OpenAI models |
| `MISTRAL_API_KEY` | - | For Mistral models |

---

## Best Practices

1. **Temperature**: Use 0.0 for deterministic outputs
2. **Memory**: Configure SurrealDB for conversation history
3. **Tools**: Keep tool functions focused and single-purpose
4. **Guardrails**: Apply post-execution for output validation
5. **Instructions**: Keep instructions concise and specific

---

## Examples

See `examples/` directory:

- `examples/basic_agent.py` - Simple agent setup
- `examples/agent_with_tools.py` - Agent with function calling
- `examples/pipeline_orchestration.py` - Multi-agent pipeline
- `examples/guardrail_integration.py` - Guardrail patterns
