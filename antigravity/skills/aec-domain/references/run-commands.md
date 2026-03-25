# AEC Domain Skill - Run Commands

How to run evaluations and use this skill.

---

## Running Output Quality Evals

Use the skill-evaluator workflow:

1. Load the aec-domain skill
2. Read `evals/evals.json` to understand test cases
3. For each eval, write the code and verify it meets expectations

---

## Running Triggering Evals

Triggering tests require Claude Code:

```bash
cd ~/.config/opencode/skills/skill-evaluator
python scripts/run_eval.py --skill aec-domain
```

---

## Testing Locally

### Unit Tests

```bash
cd /Users/marchansen/GitHub/Cover-Architectural/onto-aec
python -m pytest tests/unit/test_tools/test_aec_validator.py -v
```

---

## Example: Validating a Concept

```python
from src.tools.aec_validator import AECDomainValidator, RuleResult

validator = AECDomainValidator()

concept = {
    "constraint_deontic": "SHALL",
    "applicable_occupancy_groups": ["A1", "A2"],
    "source_section": "3.2.1",
}

result = validator.check_v001(concept)
print(f"Passed: {result.passed}")
print(f"Message: {result.message}")
```
