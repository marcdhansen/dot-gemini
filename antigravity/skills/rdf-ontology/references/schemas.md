# RDF/OWL Skill References

Reference materials for RDF/OWL ontology development.

---

## Namespace Prefixes

```python
from rdflib import Namespace

# ONTO-AEC namespaces
AECO = Namespace("https://onto-aec.org/ontology/")
NBC = Namespace("https://onto-aec.ca/nbc/2025/")

# Standard namespaces
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
DCT = Namespace("http://purl.org/dc/terms/")
SCHEMA = Namespace("https://schema.org/")

# Building standards
IFC = Namespace("https://standards.buildingsmart.org/IFC/4.3/")
OMNICLASS = Namespace("http://www.omniclass.org/")
UNIFORMAT = Namespace("http://www.omniclass.org/tables/21/")
MASTERFORMAT = Namespace("http://www.omniclass.org/tables/22/")
```

---

## Common Predicates

| Predicate | Usage |
|-----------|-------|
| `RDF.type` | Class membership (`rdf:type`) |
| `RDFS.subClassOf` | Class hierarchy |
| `RDFS.label` | Human-readable label |
| `RDFS.comment` | Documentation |
| `RDFS.isDefinedBy` | Definition source |
| `OWL.equivalentClass` | Class equivalence |
| `OWL.disjointWith` | Class disjointness |
| `OWL.hasProperty` | Property definition |
| `SKOS.exactMatch` | High-confidence alignment (≥0.90) |
| `SKOS.closeMatch` | Medium-confidence (0.70-0.89) |
| `SKOS.broadMatch` | Broader concept |
| `SKOS.narrowMatch` | Narrower concept |
| `DCT.source` | Source document reference |

---

## Validation Rule Details

### V-006: IFC Namespace Isolation

```python
IFC_NS_PREFIXES = (
    "https://standards.buildingsmart.org/IFC/",
    "http://www.buildingsmart-tech.org/ifc/",
    "https://www.buildingsmart.org/",
)

def assert_no_ifc_iri(iri: str):
    """V-006: Raise if IRI uses IFC namespace."""
    for prefix in IFC_NS_PREFIXES:
        if iri.startswith(prefix):
            raise ValueError(f"V-006 violation: {iri}")
```

### V-002: Fire Rating Monotonicity

Subclasses must have fire ratings ≥ parent:
- Parent: 2-hour rating
- Child: Must be 2-hour or higher (1-hour would be violation)

---

## SHACL Shapes Location

```
shapes/
├── onto-core-shapes.ttl    # Core ontology shapes
├── onto-occupancy-shapes.ttl  # Occupancy-specific
├── onto-structural-shapes.ttl # Structural constraints
└── onto-validation-shapes.ttl # Domain rules
```

---

## Dependencies

Install all required packages:

```bash
pip install rdflib==7.0.0 pyshacl==0.26.0 owlrl==6.0.2 rdflib-jsonld==0.6.2
```

---

## Serialization Formats

```python
from rdflib import Graph

g = Graph()

# Serialize to different formats
turtle_output = g.serialize(format="turtle")
xml_output = g.serialize(format="xml")
n3_output = g.serialize(format="n3")
nt_output = g.serialize(format="nt")
jsonld_output = g.serialize(format="json-ld")
```
