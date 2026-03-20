---
name: surrealdb
description: >
  SurrealDB operations for ONTO-AEC. Provides async database patterns, schema management,
  and query optimization for the ontology construction platform. Use when working with
  SurrealDB connection setup, CRUD operations on ontology data, schema migrations, or
  cache management.
compatibility: >
  Requires Python 3.10+, surrealdb Python SDK 1.0.8+, and access to SurrealDB instance.
  Inline evaluation works in any environment with the SDK installed.
metadata:
  author: ONTO-AEC Team
  version: 1.0.0
  category: database
  tags: [surrealdb, async, ontology, database, schema, migration]
  dependencies: [skill-evaluator]
---

# SurrealDB Skill

Provides SurrealDB operations for the ONTO-AEC ontology construction platform.

## When to Use

- Connecting to SurrealDB instances (ontology namespace, agent memory namespace)
- CRUD operations on ontology data (concepts, properties, relationships)
- Schema definition and migrations
- Redis-backed caching with SurrealDB persistence
- Query optimization and transaction management

**Do not use for**: General SQL databases, relational data modeling, or non-async contexts.

---

## ONTO-AEC Data Model

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `onto_ontology` | Ontology metadata | `ontology_id`, `name`, `base_iri`, `source_document_id` |
| `onto_concept` | Concept nodes | `concept_id`, `iri`, `label_primary`, `concept_type`, `risk_tier` |
| `onto_property` | Property nodes | `property_id`, `iri`, `property_type`, `domain_concept_iri` |
| `onto_relationship` | Relationship edges | `from_concept_iri`, `to_concept_iri`, `relation_type`, `confidence` |
| `onto_job` | Processing jobs | `job_id`, `status`, `ontology_id`, `created_at` |
| `onto_alignment` | Standard alignments | `concept_iri`, `standard`, `aligned_iri`, `match_type`, `confidence` |
| `onto_review` | Human review queue | `item_id`, `item_type`, `status`, `reviewer`, `created_at` |

### Connection Pattern

```python
from src.db.surreal_client import get_surreal_client

async def get_ontology_db():
    """Returns AsyncSurreal client connected to NS:aec DB:ontology."""
    return await get_surreal_client()
```

---

## Common Patterns

### Basic CRUD Operations

```python
from surrealdb import AsyncSurreal
from surrealdb.engine import RecordID

async def create_ontology(db: AsyncSurreal, ontology_data: dict):
    """Create a new ontology record."""
    result = await db.create("onto_ontology", ontology_data)
    return result[0]

async def get_concept(db: AsyncSurreal, concept_id: str):
    """Retrieve a concept by ID."""
    return await db.select(f"onto_concept:{concept_id}")

async def update_concept(db: AsyncSurreal, concept_id: str, updates: dict):
    """Update concept fields."""
    return await db.merge(RecordID("onto_concept", concept_id), updates)

async def delete_relationship(db: AsyncSurreal, rel_id: str):
    """Delete a relationship."""
    await db.delete(f"onto_relationship:{rel_id}")
```

### Query Operations

```python
async def find_concepts_by_type(db: AsyncSurreal, concept_type: str):
    """Find all concepts of a specific type."""
    return await db.query(
        "SELECT * FROM onto_concept WHERE concept_type = $type",
        {"type": concept_type}
    )

async def get_related_concepts(db: AsyncSurreal, concept_iri: str):
    """Get all concepts related to a given concept."""
    return await db.query("""
        SELECT * FROM onto_relationship 
        WHERE from_concept_iri = $iri OR to_concept_iri = $iri
    """, {"iri": concept_iri})

async def search_concepts(db: AsyncSurreal, label: str):
    """Search concepts by label (case-insensitive)."""
    return await db.query("""
        SELECT * FROM onto_concept 
        WHERE string::lowercase(label_primary) CONTAINS string::lowercase($label)
    """, {"label": label})
```

### Transaction Patterns

```python
async def atomic_concept_update(db: AsyncSurreal, concept_id: str, updates: dict):
    """Atomic update within a transaction."""
    async with db.transaction():
        current = await db.select(f"onto_concept:{concept_id}")
        if current:
            await db.merge(RecordID("onto_concept", concept_id), updates)
```

---

## Schema Management

### Defining Tables

```sql
-- Core ontology table
DEFINE TABLE onto_ontology SCHEMAFULL;
DEFINE FIELD ontology_id ON onto_ontology TYPE string;
DEFINE FIELD name ON onto_ontology TYPE string;
DEFINE FIELD base_iri ON onto_ontology TYPE string;
DEFINE FIELD description ON onto_ontology TYPE option<string>;
DEFINE FIELD domain ON onto_ontology TYPE string DEFAULT 'general';
DEFINE FIELD source_document_id ON onto_ontology TYPE string;
DEFINE FIELD version ON onto_ontology TYPE string DEFAULT '1.0.0';
DEFINE INDEX idx_ontology_id ON onto_ontology FIELDS ontology_id UNIQUE;

-- Concept table
DEFINE TABLE onto_concept SCHEMAFULL;
DEFINE FIELD concept_id ON onto_concept TYPE string;
DEFINE FIELD iri ON onto_concept TYPE string;
DEFINE FIELD label_primary ON onto_concept TYPE string;
DEFINE FIELD label_secondary ON onto_concept TYPE option<string>;
DEFINE FIELD definition ON onto_concept TYPE string;
DEFINE FIELD concept_type ON onto_concept TYPE string;
DEFINE FIELD risk_tier ON onto_concept TYPE option<int>;
DEFINE FIELD source_section ON onto_concept TYPE string;
DEFINE INDEX idx_concept_iri ON onto_concept FIELDS iri UNIQUE;
```

### Migration Pattern

```python
async def migrate_add_field(db: AsyncSurreal, table: str, field: str, field_type: str):
    """Add a new field to an existing table."""
    await db.query(f"DEFINE FIELD {field} ON {table} TYPE {field_type}")
```

---

## Error Handling

```python
from surrealdb.exceptions import SurrealDBException

async def safe_query(db: AsyncSurreal, query: str, params: dict = None):
    """Execute query with error handling."""
    try:
        result = await db.query(query, params or {})
        return result
    except SurrealDBException as e:
        logger.error(f"SurrealDB query failed: {e}")
        raise
```

---

## Redis Caching Integration

ONTO-AEC uses Redis for caching. Pattern for cache-aside:

```python
import json
import redis.asyncio as redis

CACHE_TTL = 86400  # 24 hours

async def get_cached_concept(redis_client: redis.Redis, concept_id: str, db: AsyncSurreal):
    """Get concept from cache or database."""
    cache_key = f"onto:concept:{concept_id}"
    
    # Check cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    concept = await db.select(f"onto_concept:{concept_id}")
    if concept:
        await redis_client.setex(cache_key, CACHE_TTL, json.dumps(concept))
    
    return concept
```

---

## Performance Tips

1. **Use connection pooling**: Single client instance across requests
2. **Prefer `select` over `query` for single records**: `select` uses RecordID lookup
3. **Index frequently queried fields**: `DEFINE INDEX idx_field ON table FIELDS field`
4. **Batch operations with transactions**: Group related writes
5. **Cache expensive queries**: Redis for frequently accessed data

---

## Examples

See `examples/` directory for complete working examples:

- `examples/ontology_crud.py` - Basic CRUD operations
- `examples/concept_search.py` - Search patterns
- `examples/schema_migration.py` - Schema management
