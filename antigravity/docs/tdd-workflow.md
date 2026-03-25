# TDD Workflow Guide

## Mode Selection: Turbo vs Full SOP

Choose the right mode based on task scope:

| Mode | When to Use | TDD Requirement |
|------|-------------|-----------------|
| **Turbo** | Internal tools, quick fixes, ad-hoc improvements | Minimal - stub or exempt |
| **Full SOP** | New features, external-facing, multi-session work | Full Red→Green→Refactor |

### Turbo Mode Indicators
- Internal tooling (like `tdd-check` itself)
- Single session completion expected
- No external dependencies or users
- <30 min estimated work

### Full SOP Indicators
- User-facing features
- Requires planning/approval
- Multiple sessions expected
- Tests required for quality gates

## Progressive Disclosure by Task Complexity

Based on task complexity and estimated time, apply appropriate TDD requirements:

| Complexity | Time Estimate | TDD Requirement | Example |
|------------|---------------|-----------------|---------|
| **Trivial** | <5 min | **Exempt** | Typos, docs fixes, config changes |
| **Small** | 5-30 min | **Test stub** | Simple utility functions, small features |
| **Medium** | 30 min - 2 hr | **Full TDD** | New modules, API integrations |
| **Large** | >2 hr | **Full TDD + Planning** | Epic features, architecture changes |

## Quick Reference

### Before Creating New Code

```bash
# Check if test exists (prompts if missing)
tdd-check src/agent_harness/new_module.py
```

### Exempting a File

For trivial changes that don't need tests:
```bash
tdd-check src/agent_harness/config.py --exempt --reason "Config only, no logic"
```

### Test Stub Template

When tdd-check creates a test stub:
```python
"""Tests for module_name.py."""

import pytest
from agent_harness.module_name import ClassName


class TestClassName:
    """Test cases for ClassName."""
    
    def test_placeholder(self):
        """Placeholder test - implement based on requirements."""
        pass
```

## When to Use Each Level

### Trivial (<5 min)
- Documentation fixes
- Typo corrections
- Configuration changes
- Comment updates
- **Action**: Use exemption

### Small (5-30 min)
- Small utility functions
- Simple wrappers
- Minor bug fixes
- **Action**: Run `tdd-check` - creates stub if missing

### Medium (30 min - 2 hr)
- New classes/modules
- API integrations
- Feature additions
- **Action**: Full Red → Green → Refactor

### Large (>2 hr)
- New subsystems
- Architecture changes
- Complex features
- **Action**: Full SOP + TDD + Planning

## TDD Commands

```bash
# Pre-check before coding
tdd-check <file>

# Exempt from TDD
tdd-check <file> --exempt --reason "..."

# List exemptions
cat ~/.agent/tdd-exemptions.json
```

## Enforcement

- **Pre-implementation**: Run `tdd-check` before first code change
- **Finalization**: SOP checks for test coverage
- **Exemptions**: Logged and auditable

## Examples

### Small Feature (Test Stub)
```bash
$ tdd-check src/agent_harness/utils.py
⚠ No test found for utils.py
Expected test locations:
  - test_utils.py
  - utils_test.py
  - tests/test_utils.py

Create test now? [y/N] y
✓ Created test stub: test_utils.py
```

### Trivial Fix (Exemption)
```bash
$ tdd-check docs/README.md --exempt --reason "Documentation only"
✓ Exemption added for docs/README.md
```

### Medium Feature (Full TDD)
```bash
# 1. Write failing test
$ echo 'def test_new_feature(): assert new_func() == expected' > tests/test_new_feature.py

# 2. Run to see failure
$ pytest tests/test_new_feature.py -v

# 3. Implement
# ... write code ...

# 4. Run to see pass
$ pytest tests/test_new_feature.py -v
```
