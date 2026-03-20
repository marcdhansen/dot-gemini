# Phase 5: Finalization

> **Status**: **MANDATORY** — Must complete before session end  
> **Skill**: `/finalization`  
> **Validation**: `check_protocol_compliance.py --finalize`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Ensure all work is committed, quality gates passed, PR created, and context preserved.

---

## ⚠️ CRITICAL: PR Required

> **All code changes MUST have a PR created**  
> Another agent must review and approve before merge.

---

## Quick Checklist

- [ ] **Quality Gates**: Run linters, tests, pre-commit hooks
- [ ] **Git Sync**: Commit all changes, squash into atomic commit
- [ ] **🔒 PR Creation**: Create Pull Request for the feature branch
- [ ] **Beads Update**: Update/close issues appropriately
- [ ] **Orchestrator Check**: `check_protocol_compliance.py --finalize`

---

## Detailed Requirements

### Quality Gates

```bash
# Python
uv run ruff check --fix . && uv run ruff format .

# Unified
pre-commit run --all-files
```

- [ ] All tests pass
- [ ] Linting passes
- [ ] Build succeeds (if applicable)

### Git Operations

- [ ] Stage all changes: `git add .`
- [ ] Commit with descriptive message
- [ ] Squash into atomic commit
- [ ] Push to remote: `git push`
- [ ] **Create PR**: `gh pr create --fill`

### PR Review Issue

- [ ] Create P0 beads issue: `bd create --priority P0 "PR Review: [branch-name]"`
- [ ] Include PR link in issue description
- [ ] Issue must invoke `/code-review` skill

### Beads Update

- [ ] Close completed tasks
- [ ] Add closure notes to issues
- [ ] Create issues for remaining work

---

## Orchestrator Validation

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize
```

---

*[← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
