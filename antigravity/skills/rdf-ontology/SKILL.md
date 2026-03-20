---
name: rdf-ontology
description: >
  RDF/OWL ontology development for ONTO-AEC. Provides rdflib graph construction, SHACL
  validation, OWL reasoning, and multi-format serialization. Use when building ontologies,
  validating RDF data, reasoning over OWL axioms, or exporting to standards-aligned formats.
compatibility: >
  Requires Python 3.10+, rdflib 7.0.0+, pyshacl 0.26.0+, owlrl 6.0.2+.
  Inline evaluation works in any environment with dependencies installed.
metadata:
  author: ONTO-AEC Team
  version: 1.0.0
  category: ontology
  tags: [rdf, owl, ontology, rdflib, shacl, validation, serialization]
  dependencies: [skill-evaluator]
---

# RDF/OWL Ontology Skill

Provides RDF/OWL ontology operations for the ONTO-AEC platform.

## When to Use

- Building RDF graphs from ontology data
- SHACL validation of ontology constraints
- OWL reasoning over ontology axioms
- Multi-format serialization (9 formats)
- Cycle detection in subclass hierarchies
- Standards alignment (IFC, OmniClass, UniFormat)

**Do not use for**: General data modeling, non-RDF formats, or graph algorithms.

---

## Core Technologies

| Library | Version | Purpose |
|---------|---------|---------|
| rdflib | 7.0.0 | RDF graph manipulation |
| pyshacl | 0.26.0 | SHACL constraint validation |
| owlrl | 6.0.2 | OWL 2 RL reasoning |
| rdflib-jsonld | 0.6.2 | JSON-LD serialization |

---

## Common Patterns

### Building an RDF Graph

```python
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SKOS

AECO = Namespace("https://onto-aec.org/ontology/")
NBC = Namespace("https://onto-aec.ca/nbc/2025/")

def build_ontology_graph(ontology_data: dict) -> Graph:
    """Build an RDF graph from ontology data."""
    g = Graph()
    
    # Bind namespaces
    g.bind("aeco", AECO)
    g.bind("owl", OWL)
    g.bind("skos", SKOS)
    
    # Add ontology metadata
    ontology_uri = AECO[ontology_data["ontology_id"]]
    g.add((ontology_uri, RDF.type, OWL.Ontology))
    g.add((ontology_uri, RDFS.label, Literal(ontology_data["name"])))
    g.add((ontology_uri, AECO.baseIri, URIRef(ontology_data["base_iri"])))
    
    # Add concepts
    for concept in ontology_data.get("concepts", []):
        concept_uri = AECO[concept["concept_id"]]
        g.add((concept_uri, RDF.type, OWL.Class))
        g.add((concept_uri, RDFS.label, Literal(concept["label_primary"])))
        g.add((concept_uri, RDFS.isDefinedBy, URIRef(concept["iri"])))
        
        if concept.get("definition"):
            g.add((concept_uri, RDFS.comment, Literal(concept["definition"])))
    
    return g
```

### Adding Relationships

```python
def add_relationships(g: Graph, relationships: list):
    """Add relationships to an RDF graph."""
    AECO = Namespace("https://onto-aec.org/ontology/")
    
    for rel in relationships:
        from_uri = AECO[rel["from_concept_iri"]]
        to_uri = AECO[rel["to_concept_iri"]]
        
        if rel["relation_type"] == "subClassOf":
            g.add((from_uri, RDFS.subClassOf, to_uri))
        elif rel["relation_type"] == "equivalentClass":
            g.add((from_uri, OWL.equivalentClass, to_uri))
        elif rel["relation_type"] == "skos:exactMatch":
            g.add((from_uri, SKOS.exactMatch, to_uri))
        # ... other relation types
```

### SHACL Validation

```python
from src.tools.shacl_tools import run_shacl_validation, parse_shacl_violations

def validate_ontology(data_graph: Graph) -> dict:
    """Validate ontology against SHACL shapes."""
    conforms, report_text, results_graph = run_shacl_validation(data_graph)
    
    violations = parse_shacl_violations(results_graph)
    
    return {
        "conforms": conforms,
        "violation_count": len(violations),
        "violations": violations,
        "report": report_text
    }
```

### OWL Reasoning

```python
import owlrl

def reason_ontology(g: Graph) -> Graph:
    """Apply OWL 2 RL reasoning to expand the graph."""
    # Create a closure graph (doesn't modify original)
    closure_graph = g + Graph()
    
    # Apply OWL 2 RL rules
    owlrl.DeductiveClosure(owlrl.OWL2RL).expand(closure_graph)
    
    return closure_graph
```

### Serialization (9 Formats)

```python
from src.tools.rdf_builder import serialize_graph

def export_ontology(g: Graph, format: str, output_path: str):
    """Export graph in specified format."""
    # Supported: turtle, xml, n3, nt, json-ld, owlxml
    serialize_graph(g, output_path, format=format)
```

---

## Supported Serialization Formats

| Format | Extension | MIME Type | Use Case |
|--------|-----------|-----------|----------|
| Turtle | `.ttl` | `text/turtle` | Human-readable |
| RDF/XML | `.rdf` | `application/rdf+xml` | Standard interchange |
| N3 | `.n3` | `text/n3` | Notation3 |
| N-Triples | `.nt` | `application/n-triples` | Line-based |
| JSON-LD | `.jsonld` | `application/ld+json` | Web APIs |
| OWL/XML | `.owx` | `application/owl+xml` | OWL tooling |

---

## Validation Rules (V-001 to V-015)

ONTO-AEC implements AEC domain validation:

| Rule | Severity | Description |
|------|----------|-------------|
| V-001 | CRITICAL | Deontic Completeness - SHALL/SHALL_NOT requires occupancy groups |
| V-002 | ERROR | Fire Rating Monotonicity - subclass rating ≥ parent |
| V-003 | ERROR | Occupancy Group Closed World |
| V-004 | ERROR | Cross-Reference Resolution |
| V-005 | CRITICAL | Structural Load Disjointness |
| V-006 | CRITICAL | IFC Namespace Isolation |
| V-007 | ERROR | Source Traceability |
| V-008 | WARNING | Bilingual Label Non-Identity |
| V-009 | ERROR | Edition Year Coherence |
| V-010 | ERROR | Prescriptive/Performance Disjointness |
| V-011 | ERROR | Prohibition Condition Completeness |
| V-012 | WARNING | Numeric Property Bounds |
| V-013 | WARNING | Deprecated Concept Successor |
| V-014 | CRITICAL | Alignment Strength Gate |
| V-015 | ERROR | Section Boundary Respect |

---

## Standards Alignment

### Supported Standards

| Standard | Namespace | Purpose |
|----------|-----------|---------|
| IFC 4.3 | `https://standards.buildingsmart.org/IFC/` | Building data |
| OmniClass | `http://www.omniclass.org/` | Construction classification |
| UniFormat | OmniClass Table 21 | Uniformat |
| MasterFormat | OmniClass Table 22 | MasterFormat |

### Alignment Relations

```python
# Standard alignment patterns
g.add((concept_uri, SKOS.exactMatch, standard_uri))      # ≥0.90 confidence
g.add((concept_uri, SKOS.closeMatch, standard_uri))      # 0.70-0.89
g.add((concept_uri, SKOS.broadMatch, standard_uri))       # broader
g.add((concept_uri, SKOS.narrowMatch, standard_uri))     # narrower
```

---

## Examples

See `examples/` directory:

- `examples/build_graph.py` - Basic graph construction
- `examples/shacl_validation.py` - Constraint validation
- `examples/serialize_formats.py` - Multi-format export
- `examples/standards_alignment.py` - IFC/OmniClass alignment
