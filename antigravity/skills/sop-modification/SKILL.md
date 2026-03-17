---
name: sop-modification
description: >
  Best practices for SOP enforcement, with TDD-first workflows for modifying
  mandatory SOP gates. Use whenever modifying mandatory quality gates,
  phase transitions, or compliance requirements in the SOP — ensures changes
  are testable and enforced, not just documented.
  Do NOT use for general TDD guidance (use the tdd skill instead) or for
  code changes unrelated to SOP gates or SOP infrastructure.
compatibility: >
  Requires Python 3.x and access to SOP infrastructure files. Scripts live
  in ~/.gemini/antigravity/skills/sop-modification/scripts/.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: process
  tags: [sop, tdd, gates, compliance, process-modification]
---

# 🛡️ SOP Modification Skill

> **Purpose**: Enforce TDD practices when modifying mandatory SOP gates, preventing unenforceable rules and closing loopholes.  
> **Mandatory Use**: This skill MUST be invoked whenever modifying mandatory SOP gates.  
> **Prerequisite**: Use the `/tdd` skill for general TDD guidance.

## Scope

This skill applies to two categories of SOP modifications:

### 1. Mandatory Gate Changes (TDD Required)

Modifications involving **mandatory gates**:

- Quality gates (TDD compliance, atomic commits, clean git)
- Phase transitions (Initialization → Planning → Execution → Finalization)
- Compliance requirements (Beads issues, reflection capture, plan approval)

**Requirements**: TDD-first workflow (Red → Green → Refactor)

### 2. SOP Infrastructure Code Changes (Full SOP Required)

Code changes to **SOP infrastructure**:

- Orchestrator scripts (`~/.gemini/antigravity/skills/Orchestrator/scripts/`)
- Skill scripts (`~/.gemini/antigravity/skills/*/scripts/`)
- SKILL.md files
- SOP documentation (`~/.agent/docs/SOP_COMPLIANCE_CHECKLIST.md`, `~/.agent/docs/sop/`)

**Requirements**: Full SOP process (feature branch, PR, code review) + TDD if modifying gates

> [!IMPORTANT]
> **Automatic Escalation**: The Orchestrator automatically detects SOP infrastructure changes and blocks Turbo Mode, requiring Full Mode (`--init`).

Changes to explanatory text, examples, or non-gate documentation do NOT require this skill.

---

## SOP Gate Modification Workflow (TDD-First)

### 1. Identify the Gate

Determine if the change involves a mandatory requirement (`MANDATORY`, `MUST`, `BLOCKER`, `🔒`).

### 2. Red Phase: Write Failing Gate Tests

Before modifying the SOP documentation or the Orchestrator, create a test that verifies the new rule is currently violated (or not yet enforced).

- **Location**: `tests/gatekeeper/test_sop_gate_{name}.py`
- **Use**: `python ~/.gemini/antigravity/skills/sop-modification/scripts/generate_test_template.py` to get started.

Run the test to confirm it **FAILS**:

```bash
pytest tests/gatekeeper/test_sop_gate_{name}.py
```

### 3. Green Phase: Implement SOP Rule & Enforcement

1. Update the SOP documentation in `~/.agent/docs/`.
2. Update the Orchestrator logic in `~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py`.

Run the test again to confirm it **PASSES**:

```bash
pytest tests/gatekeeper/test_sop_gate_{name}.py
```

### 4. Refactor & Loophole Analysis

Clean up the enforcement logic. Perform a **loophole analysis**:

- Identify workarounds (e.g., can an agent bypass the check by changing a file name?)
- Add tests for these loopholes.
- Document identified loopholes in `templates/sop_change_checklist.md`.

---

## Best Practices for SOP Enforcement

### 1. Make Gates Programmatic

Whenever possible, enforcement should be automated via the Orchestrator or pre-commit hooks. Avoid "social contract" rules that have no automated validation.

### 2. Test Negative Scenarios

Ensure your tests verify that violations ARE caught. A gate that always passes is not a gate; it's a decorator.

### 3. Clear Failure Messages

When a gate blocks work, it MUST provide:

- Clear reason for the block.
- Actionable steps to resolve the issue.
- Link to the relevant SOP documentation.

### 4. Linear history

Always maintain a clean, linear git history. Mandatory gates ensure that only atomic, compliant commits reach the main branch.

---

## Tools & Templates

- **`validate_sop_change.py`**: Pre-commit hook to block gate changes without tests.
- **`generate_test_template.py`**: Generates test stubs for new gates.
- **`check_test_coverage.py`**: Reports coverage of mandatory gates.
- **`sop_change_checklist.md`**: Template for documenting gate changes.

---

## Enforcement

The Orchestrator will automatically invoke this skill if it detects modifications to SOP gate files during initialization. Work will be blocked if corresponding tests are not found.
