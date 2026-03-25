# Session Handoff Format

Standard format for handing off work between sessions or agents.

## Handoff File Location

```
.agent/handoffs/{session-id}-session.md
```

Example: `.agent/handoffs/001-universal-agent-session.md`

## Required Sections

```markdown
# Session Handoff

## Session Info
- **Date**: 2026-03-24
- **Session ID**: {uuid}
- **Branch**: feature/my-branch

## What Was Accomplished
- [ ] Created initial structure
- [ ] Implemented core feature
- [ ] Added tests

## Active Tasks
| ID | Description | Status |
|----|-------------|--------|
| 1  | Write more tests | in_progress |
| 2  | Update docs | pending |

## Files Changed
- `src/main.py` - Added feature X
- `tests/test_main.py` - Added tests

## Next Steps
1. Continue with remaining tests
2. Run quality gates
3. Create PR

## Notes for Next Session
- API key needs rotation
- Tests are flaky on CI
```

## Quick Handoff (Minimal)

If you only have time for a quick handoff:

```markdown
# Quick Handoff

**What done**: Feature implementation complete
**What's left**: Tests, docs, PR
**Key file**: src/feature.py
**Blockers**: None
```

## Handoff Checklist

Before ending session, verify:
- [ ] Handoff file created
- [ ] All active tasks documented
- [ ] Next steps clear
- [ ] Blockers noted
- [ ] Key files listed
