# Phase 2: Initialization

> **Status**: **MANDATORY** — Orchestrator blocks if incomplete  
> **Validation**: `check_protocol_compliance.py --init`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Verify all prerequisites are met before starting work. Ensures tools, context, and approvals are in place.

---

## Quick Checklist

- [ ] **Tool Check**: Verify required tools (`bd`, `uv`, `git`)
- [ ] **Context Check**: Read `ROADMAP.md` and `ImplementationPlan.md`
- [ ] **Status Check**: Run `bd ready` to see active tasks
- [ ] **Issue Check**: Run `bd ready` (Optional for planning, highly recommended)
- [ ] **Navigation Check**: Verify access to documentation
- [ ] **Plan Approval**: Confirm plan approved within 4 hours
- [ ] **Progress Log Discovery**: Check for `{issue-id}.md` in `~/.agent/progress-logs/`
- [ ] **Orchestrator Check**: Run `check_protocol_compliance.py --init`

---

## Detailed Requirements

### Tool Check

- [ ] `bd` — Beads task management available
- [ ] `uv` — Python package manager available
- [ ] `git` — Version control available
- [ ] Project-specific tools as configured

### Context Check

- [ ] Read `.agent/rules/ROADMAP.md` for high-level objectives
- [ ] Read `.agent/rules/ImplementationPlan.md` for current phase
- [ ] Understand current milestone and success criteria

### Status Check

- [ ] Run `bd ready` to see unblocked tasks
- [ ] Identify task to work on
- [ ] Check for blocking dependencies

### Issue Check

- [ ] Beads issue exists for current objective (Optional for planning, highly recommended)
- [ ] If not, create with `bd create`
- [ ] Assign issue to self if working in parallel

### Plan Approval

- [ ] Implementation plan exists and is approved
- [ ] Approval timestamp is within 4 hours
- [ ] If stale, request re-approval from user

### Progress Log Discovery

- [ ] Check `~/.agent/progress-logs/{issue-id}.md` exists
- [ ] Read "Active Context" section for current state
- [ ] Review last 3-5 entries for immediate context
- [ ] Note any blockers or open questions

### Navigation Check

- [ ] Access to `~/.agent/docs/GLOBAL_INDEX.md`
- [ ] Access to project documentation
- [ ] Understand project structure

---

## Orchestrator Validation

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --init
```

### Pass Example

```text
✅ INITIALIZATION COMPLETE
├── Tools: ✅ All required tools available
├── Context: ✅ Planning documents accessible  
├── Issues: ℹ️ No Beads issue (Optional for planning)
└── Approval: ✅ Plan approved 2 hours ago

Ready to execute!
```

### Fail Example

```text
❌ INITIALIZATION BLOCKED
├── Tools: ✅ All required tools available
├── Context: ❌ ImplementationPlan.md not found
├── Issues: ✅ Beads issue assigned
└── Approval: ⚠️ Plan approval is 5 hours old (stale)

BLOCKERS:
1. Create implementation plan before proceeding
2. Re-approve plan (approval expires after 4 hours)
```

---

- [← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
