---
name: code-review
description: Checklist-based code review skill for identifying logic errors, ensuring test coverage, and validating PR size.
allowed-tools: Bash, Read, Glob, Grep
---

# 🛡️ Code Review Skill

The `code-review` skill provides automated and interactive code review capabilities for agents. It ensures that all changes meet quality standards before they are finalized.

## 🚨 MANDATORY: Finalization Gate

> [!CAUTION]
> If this skill is invoked during finalization and "Request Changes" is selected, **it MUST block Git operations (commits/pushes)** until the issues are resolved.

## Usage

```bash
/code-review
python ~/.gemini/antigravity/skills/code-review/scripts/code_review.py
```

## Purpose

This skill performs a multi-stage code review:

1. **Logic Correctness**: Analyzes diffs for potential logic errors or regressions.
2. **Test Coverage**: Verifies that new functionality includes corresponding tests.
3. **PR Size Validation**: Checks if the total changes exceed recommended thresholds (default: 500 lines).
4. **Interactive Checklist**: Prompts the agent to verify critical items.

## Implementation

- **Core Logic**: `~/.gemini/antigravity/skills/code-review/scripts/code_review.py`
- **Configuration**: `~/.gemini/antigravity/skills/code-review/config/defaults.yaml`
- **Gate Enforcement**: Integrated with Orchestrator finalization phase.

## Configuration

Default settings in `config/defaults.yaml`:

```yaml
max_diff_lines: 500
require_tests: true
block_on_request_changes: true
```

## Error Handling

- **Large Diffs**: Warns if the diff is too large for effective review.
- **Missing Tests**: Flags missing tests for new code files.
- **User Intervention**: Allows manual override if necessary (logged).

## Integration

- **Orchestrator**: Blocks finalization if the review status is `REQUEST_CHANGES`.
- **Beads**: Links review outcomes to the active task.

## P0 Review Issue Protocol

When assigned a P0 PR review issue:

1. **Read Issue**: Open the PR link from the issue description
2. **Run Review**: `python ~/.gemini/antigravity/skills/code-review/scripts/code_review.py`
3. **Complete Checklist**: Answer all interactive checklist items
4. **Document Outcome**: Update the issue with your review outcome

### Outcomes

| Decision | Action |
| --- | --- |
| **APPROVE** | Close the issue → Unblocks PR merge |
| **REQUEST_CHANGES** | Add comment with required changes → Keep issue open |

### 🚀 Merging Protocol

After approving a PR, always use the **"Squash and merge"** option on GitHub to maintain a clean atomic history.

- **Automation**: Use the `browser_subagent` to navigate to the PR URL and explicitly select "Squash and merge" from the dropdown before confirming.
- **Verification**: Ensure the final merged commit follows the conventional format and includes the issue ID.

> [!IMPORTANT]
> The reviewing agent MUST be different from the implementing agent. This is enforced by Beads task assignment.
