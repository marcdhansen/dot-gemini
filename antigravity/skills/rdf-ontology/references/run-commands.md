# RDF/OWL Skill - Run Commands

How to run evaluations and use this skill.

---

## Running Output Quality Evals

Use the skill-evaluator workflow:

1. Load the rdf-ontology skill
2. Read `evals/evals.json` to understand test cases
3. For each eval, write the code and verify it meets expectations

---

## Running Triggering Evals

Triggering tests require Claude Code:

```bash
cd ~/.config/opencode/skills/skill-evaluator
python scripts/run_eval.py --skill rdf-ontology
```

---

## Testing Locally

### Unit Tests

```bash
cd /Users/marchansen/GitHub/Cover-Architectural/onto-aec
python -m pytest tests/unit/test_tools/test_rdf_builder.py -v
python -m pytest tests/unit/test_tools/test_shacl_tools.py -v
```

### Integration Tests

```bash
# Requires SurrealDB and Redis
docker-compose up -d

# Run ontology tests
python -m pytest tests/integration/test_ontology.py -v
```

---

## Example: Building and Validating

```python
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL

AECO = Namespace("https://onto-aec.org/ontology/")

# Build graph
g = Graph()
g.bind("aeco", AECO)
g.bind("owl", OWL)

# Add ontology
onto_uri = AECO["nbc-2025"]
g.add((onto_uri, RDF.type, OWL.Ontology))
g.add((onto_uri, RDFS.label, Literal("NBC 2025")))

# Add concept
wall_uri = AECO["Concept:Wall"]
g.add((wall_uri, RDF.type, OWL.Class))
g.add((wall_uri, RDFS.label, Literal("Wall")))

# Serialize
print(g.serialize(format="turtle"))
```

---

## Dependencies

```bash
pip install rdflib==7.0.0 pyshacl==0.26.0 owlrl==6.0.2 rdflib-jsonld==0.6.2
```
