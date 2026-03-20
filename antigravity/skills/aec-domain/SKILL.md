---
name: aec-domain
description: >
  AEC (Architecture, Engineering, Construction) domain knowledge for ONTO-AEC. Provides
  validation rules, risk tier assignment, standards alignment patterns, and NBC-specific
  concepts. Use when validating ontology concepts, assigning risk tiers, or aligning with
  building standards.
compatibility: >
  Requires Python 3.10+. Inline evaluation works in any environment.
metadata:
  author: ONTO-AEC Team
  version: 1.0.0
  category: domain
  tags: [aec, building-code, validation, risk-tier, standards, nbc, ifc]
  dependencies: [skill-evaluator, rdf-ontology]
---

# AEC Domain Skill

Provides AEC domain knowledge and validation rules for ONTO-AEC.

## When to Use

- Validating ontology concepts against AEC domain rules
- Assigning risk tiers to concepts
- Standards alignment (IFC, OmniClass, UniFormat)
- Understanding NBC structure and occupancy groups
- Fire rating and structural load validation

**Do not use for**: General software validation, non-AEC domains, or non-building-code contexts.

---

## Validation Rules (V-001 to V-015)

The platform implements 15 AEC domain validation rules:

| Rule | Severity | Description |
|------|----------|-------------|
| V-001 | CRITICAL | Deontic Completeness - SHALL/SHALL_NOT requires occupancy groups |
| V-002 | ERROR | Fire Rating Monotonicity - subclass rating ≥ parent |
| V-003 | ERROR | Occupancy Group Closed World - all subclasses present |
| V-004 | ERROR | Cross-Reference Resolution - skos:related must resolve |
| V-005 | CRITICAL | Structural Load Disjointness - one category only |
| V-006 | CRITICAL | IFC Namespace Isolation - no IFC prefixes in concept IRIs |
| V-007 | ERROR | Source Traceability - dct:source required |
| V-008 | WARNING | Bilingual Label Non-Identity - labels must differ |
| V-009 | ERROR | Edition Year Coherence - same year across ontology |
| V-010 | ERROR | Prescriptive/Performance Disjointness - exactly one path |
| V-011 | ERROR | Prohibition Condition Completeness - SHALL_NOT needs constraints |
| V-012 | WARNING | Numeric Property Bounds - values in valid ranges |
| V-013 | WARNING | Deprecated Concept Successor - superseded relationship |
| V-014 | CRITICAL | Alignment Strength Gate - equivalentClass ≥ 0.95, exactMatch ≥ 0.90 |
| V-015 | ERROR | Section Boundary Respect - no cross-domain properties |

---

## Risk Tier Assignment

Risk tiers govern confidence thresholds and validation stringency:

| Tier | Category | Domain | Min Confidence |
|------|----------|--------|----------------|
| 1 | Life Safety | Fire, egress, structural, accessibility | 0.95 |
| 2 | Code Compliance | Occupancy, height/area limits, sprinklers | 0.85 |
| 3 | Performance | Energy, acoustics, HVAC | 0.75 |
| 4 | Administrative | Definitions, scope, references | 0.65 |

### Assignment Rules

```python
def assign_risk_tier(concept: dict) -> int:
    """Assign risk tier based on concept properties."""
    
    # Tier 1: fire/egress/structural/accessibility sections
    section = concept.get("source_section", "").lower()
    if any(kw in section for kw in ["fire", "egress", "structural", "accessibility"]):
        return 1
    
    # Tier 1 or 2: SHALL + occupancy-scoped
    if concept.get("constraint_deontic") in ("SHALL", "SHALL_NOT"):
        if concept.get("applicable_occupancy_groups"):
            return 1
    
    # Tier 4: scope/definitions
    if any(kw in section for kw in ["scope", "definition", "reference"]):
        return 4
    
    # Default: Tier 3
    return 3
```

---

## NBC Occupancy Groups

| Group | Description |
|-------|-------------|
| A1 | Assembly - Group A (clubs, lodges) |
| A2 | Assembly - Group A (restaurants, taverns) |
| A3 | Assembly - Group A (churches, theaters) |
| A4 | Assembly - Group A (arenas, pools) |
| B1 | Business - Group B (office buildings) |
| B2 | Business - Group B (professional services) |
| B3 | Business - Group B (data processing) |
| C | Residential - Group C (apartments) |
| D | Residential - Group D (hotels, motels) |
| E | Retail - Group E (stores) |
| F1 | Industrial - Group F1 (moderate hazard) |
| F2 | Industrial - Group F2 (low hazard) |
| F3 | Industrial - Group F3 (low hazard, accessory) |

---

## Structural Load Categories

```python
LOAD_CATEGORIES = frozenset({
    "dead_load",      # Permanent loads from building weight
    "live_load",      # Occupant/occupancy loads
    "snow_load",      # Snow accumulation
    "wind_load",      # Wind pressure
    "earthquake_load", # Seismic forces
    "rain_load",      # Rain water
    "flood_load",     # Flood water
    "soil_load",      # Lateral earth pressure
    "thermal_load",   # Temperature-induced forces
    "impact_load",    # Dynamic impact forces
})
```

---

## Numeric Property Bounds

Valid ranges for AEC properties:

```python
NUMERIC_BOUNDS = {
    "minimumFireResistanceRating": (0, 240),  # minutes
    "fire_resistance_rating": (0, 240),
    "buildingHeightLimit": (0, 500),  # meters
    "floorAreaLimit": (0, 500000),  # sq meters
    "occupantLoad": (0, 10000),
    "exitWidthMinimum": (0.0, 10.0),  # meters
}
```

---

## Standards Alignment

### IFC (Industry Foundation Classes)

```python
IFC_NS_PREFIXES = (
    "http://www.buildingsmart-tech.org/ifcOWL/",
    "https://standards.buildingsmart.org/IFC/",
    "http://www.buildingsmart-tech.org/ifc/",
    "https://www.buildingsmart.org/",
)

# V-006: Concepts must NOT use IFC namespace
# Use project-specific namespaces instead
```

### OmniClass Tables

| Table | Name | Use Case |
|-------|------|----------|
| 11 | Construction Entities | Elements |
| 13 | Properties | Attributes |
| 21 | UniFormat | Cost estimating |
| 22 | MasterFormat | Project organization |
| 23 | OmniClass Numbers | Classification |

---

## Common Patterns

### Validating a Concept

```python
from src.tools.aec_validator import AECDomainValidator

validator = AECDomainValidator()

# Validate a concept
result = validator.check_v001(concept)

if not result.passed:
    print(f"V-001 violation: {result.message}")
    print(f"Suggested fix: {result.suggested_fix}")
```

### Applying All Rules

```python
def validate_ontology(ontology_graph: OntologyGraph) -> List[RuleResult]:
    """Run all V-001 through V-015 checks."""
    validator = AECDomainValidator()
    results = []
    
    for concept in ontology_graph.concepts:
        results.append(validator.check_v001(concept))
        results.append(validator.check_v002(concept))
        # ... all rules
    
    return results
```

---

## Examples

See `examples/` directory:

- `examples/risk_tier_assignment.py` - Automatic tier assignment
- `examples/validate_fire_rating.py` - V-002 monotonicity check
- `examples/standards_alignment.py` - IFC/OmniClass alignment
