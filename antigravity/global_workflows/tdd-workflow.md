---
description: Spec-Driven Test-Driven Development (TDD) Workflow
---

# 🧪 Spec-Driven TDD Workflow

This workflow ensures that every functional change is verified by a test before any implementation code is written.

## 1. Specification Phase

Define the requirements and success criteria in your planning documents.

- Update `ImplementationPlan.md` with the specific feature/bug logic.
- Ensure a Beads ID exists for the task.

## 2. Red Phase (Failure)

Create a test case that reproduces the bug or verifies the new feature.

- **Python**: Add a test in `tests/` (e.g., `tests/test_feature_name.py`).
- **WebUI**: Add a Playwright test in `lightrag_webui/tests/`.
- Run the test and confirm it **FAILS**.

```bash
# Python example
pytest tests/test_feature_name.py
# WebUI example
cd lightrag_webui && bunx playwright test tests/test_feature_name.spec.ts
```

## 3. Green Phase (Implementation)

Write the minimum code necessary to make the test pass.

- Focus on the specific task.
- Avoid scope creep.

## 4. Verification Phase (Success)

Run the test again and confirm it **PASSES**.

- Run all related tests to ensure no regressions.

## 5. Refactor Phase

Clean up the code while keeping the tests passing.

- Improve variable names, structure, and documentation.
- Run tests one last time.

## 6. Audit Phase (LLM-Specific)

For features affecting extraction or reasoning:

- Run the relevant benchmark/audit script.
- Document speed-accuracy tradeoffs in `walkthrough.md`.
