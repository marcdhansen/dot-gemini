# AEC Domain Skill References

Reference materials for AEC domain validation.

---

## Validation Rule Summary

| Rule | Severity | Category |
|------|----------|----------|
| V-001 | CRITICAL | Deontic Completeness |
| V-002 | ERROR | Fire Rating Monotonicity |
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

## Risk Tier Thresholds

```python
RISK_TIER_THRESHOLDS = {
    1: 0.95,  # Life Safety
    2: 0.85,  # Code Compliance
    3: 0.75,  # Performance
    4: 0.65,  # Administrative
}
```

---

## NBC Occupancy Groups

```python
NBC_OCCUPANCY_GROUPS = frozenset({
    "A1", "A2", "A3", "A4",
    "B1", "B2", "B3",
    "C",
    "D",
    "E",
    "F1", "F2", "F3",
})
```

---

## IFC Namespace Prefixes

```python
IFC_NS_PREFIXES = (
    "http://www.buildingsmart-tech.org/ifcOWL/",
    "https://standards.buildingsmart.org/IFC/",
    "http://www.buildingsmart-tech.org/ifc/",
    "https://www.buildingsmart.org/",
)
```

---

## Alignment Confidence Thresholds

```python
ALIGNMENT_THRESHOLDS = {
    "owl:equivalentClass": 0.95,
    "skos:exactMatch": 0.90,
    "skos:closeMatch": 0.70,
}
```
