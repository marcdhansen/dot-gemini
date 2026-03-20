# Phase 5: Finalization

> **Status**: **MANDATORY** — Must complete before session end  
> **Skill**: `/finalization`  
> **Validation**: `check_protocol_compliance.py --finalize`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Ensure all work is committed, quality gates passed, and context preserved for future sessions.

---

## Quick Checklist

- [ ] **Quality Gates**: Run linters, tests, pre-commit hooks
- [ ] **Markdown Check**: Run `markdownlint` on modified `.md` files
- [ ] **Git Sync**: Commit all changes, push to remote
- [ ] **PR Creation**: Create a Pull Request for the feature branch
- [ ] **Beads Update**: Update/close issues appropriately
- [ ] **Closure Notes**: Add implementation details to closed issues (using `bd comments add <issue-id> "note"`)
- [ ] **Orchestrator Check**: Run `check_protocol_compliance.py --finalize`

---

## Detailed Requirements

### Quality Gates

```bash
# Python
uv run ruff check --fix . && uv run ruff format .

# WebUI
cd lightrag_webui && bun run lint && bun run build

# Unified
pre-commit run --all-files
```

- [ ] All tests pass
- [ ] Linting passes
- [ ] Build succeeds (if applicable)

### Markdown Check

- [ ] Run `markdownlint` on modified `.md` files
- [ ] No duplicate markdown files in project
- [ ] All links are valid

### Git Operations

- [ ] Stage all changes: `git add .`
- [ ] Commit with descriptive message
- [ ] Sync Beads: `bd sync`
- [ ] Push to remote: `git push`
- [ ] **Create PR**: Create a GitHub Pull Request for the current branch.
  - Use `gh pr create --fill` or equivalent.
  - Ensure the PR description follows the standardized template.
- [ ] Verify: `git status` shows "up to date with origin"

### PR Review Issue Creation (MANDATORY for Full Mode)

> [!CAUTION]
> PR merge is **BLOCKED** until the review issue is closed by another agent.

After creating a rebased and squashed PR:

- [ ] Create P0 beads issue: `bd create --priority P0 "PR Review: [branch-name]"`
- [ ] Include PR link in issue description
- [ ] Issue must invoke `/code-review` skill
- [ ] Template: `~/.agent/templates/pr_review_issue_template.md`

**Turbo Mode**: This requirement is waived for Turbo Mode tasks.

### Beads Update

- [ ] Update issue status appropriately
- [ ] Close completed tasks
- [ ] Create issues for remaining work

---

## Closure Notes Template

For closed issues, add comprehensive documentation:

```markdown
## Implementation Details & Documentation

### 📁 Files Created/Modified

- `path/to/file.py` - Brief description

### 🚀 Quick Start

```bash
# Example commands
python script.py --option value
```

### 📖 Key Documentation

- **Main Docs**: `path/to/README.md#section`
- **API Reference**: `path/to/api.md`

### 🔧 Integration Points

- How it connects to existing system
- Configuration requirements

### 📊 Production Features

- Key capabilities for production use
- Monitoring and performance characteristics

```markdown
```

---

## Orchestrator Validation

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize
```

**Verifies**:

- [ ] Quality gates passed
- [ ] Git status clean
- [ ] Changes pushed to remote

---

- [← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
