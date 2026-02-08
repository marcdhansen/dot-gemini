# SOP Gate Change Checklist

> **Purpose**: Document the rationale and validation strategy for many SOP gate modifications.

## Change Overview

- **Gate Name**:
- **SOP File**:
- **Rationale**: Why is this change needed? What problem does it solve?

## Loophole Analysis

- [ ] **Direct Bypass**: Can an agent perform the action without triggering the gate?
- [ ] **State Bypass**: Can the gate be tricked by manual state manipulation?
- [ ] **Metadata Bypass**: Can changes be hidden in metadata/comments?
- [ ] **State Corruption**: Can the gate be circumvented by corrupting the session state?

**Identified Loopholes**:
1.
2.

**Mitigation Strategy**:

- How does the implementation prevent these bupasses?
- What tests were added to verify the mitigation?

## Test Strategy

- **Positive Test**: `tests/gatekeeper/test_sop_gate_{name}.py` verifies compliant state.
- **Negative Test**: `tests/gatekeeper/test_sop_gate_{name}.py` verifies violation detection.
- **Regression Test**: Added tests for previous loopholes.

## Rollback Plan

- How to revert this gate if it causes false positives or blocks critical work?
- Is there a manual override? (Ideally NO, but document if exists).

## Exemption Criteria

- List any exceptions where this gate does NOT apply.
