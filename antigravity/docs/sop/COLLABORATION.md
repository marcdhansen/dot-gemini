# 🤝 Multi-Agent Collaboration Protocol

> **Status**: **MANDATORY** — All agents operate in shared workspaces  
> **Back to**: [AGENTS.md](../../AGENTS.md) | [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## ⚠️ Golden Rules

**Memorize these — violations can corrupt shared state:**

1. **One Task, One Agent**: Never work on a task without claiming it first
2. **Branch Isolation**: Always work on `agent/<name>/task-<id>` branch
3. **Explicit Staging**: NEVER use `git add .` — stage specific files only
4. **Session Registration**: Always start with `agent-start.sh`, end with `agent-end.sh`

---

## Task & Resource Isolation

| Rule | Enforcement |
| ---- | ----------- |
| Task Exclusivity | Only one agent per task ID (hard lock) |
| Branch Naming | `agent/<name>/task-<id>` format (git hook) |
| Worktree Isolation | Separate worktree per task (auto-created) |
| Port Allocation | Unique ports per task (auto-assigned) |

---

## Session Management

```bash
# Start of session - MANDATORY
./scripts/agent-start.sh --task-id lightrag-xxx --task-desc "description"

# End of session - MANDATORY  
./scripts/agent-end.sh
```

**Session lifecycle**:

- Registration: Mandatory via `agent-start.sh`
- Heartbeat: 5-minute intervals (automatic)
- Clean end: Mandatory via `agent-end.sh`

---

## Git Safety

### Branch Protocol

```bash
# Create task branch
git checkout -b agent/gemini/task-lightrag-123

# Work...

# Merge to main via PR (never direct push)
gh pr create --fill --base main
```

### Staging Rules

```bash
# ✅ CORRECT: Stage specific files
git add tests/test_feature.py src/feature.py

# ❌ WRONG: Never use dot-add
git add .  # DANGEROUS - captures parallel work
```

---

## Conflict Prevention

| Mechanism | Description |
| --------- | ----------- |
| Git Operation Guards | Pre-commit/pre-push validation |
| Resource Lock Checking | Before any operation |
| Multi-Agent Coordination | Automatic conflict detection |
| Fail-Fast | Stop work when conflicts detected |

---

## Beads Parallel Protocol

```bash
# Claim task exclusively
bd update lightrag-123 --set-labels agent:gemini

# Sync frequently
bd sync  # At PFC start and RTB end

# Manage dependencies
bd dep lightrag-123 --blocks lightrag-124
```

---

## Quick Commands

```bash
# Validate task exclusivity
./scripts/validate_task_exclusivity.sh lightrag-xxx agent-name [check|claim|release]

# Allocate resources
./scripts/allocate_safe_resources.sh lightrag-xxx agent-name

# Session locks
./scripts/enhanced_session_locks.sh lightrag-xxx agent-name [start|end|cleanup]

# Test all systems
./scripts/test_conflict_prevention.sh
```

---

*[← Back to AGENTS.md](../../AGENTS.md)*
