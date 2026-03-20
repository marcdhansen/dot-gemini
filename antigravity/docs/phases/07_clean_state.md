# Phase 7: Clean State Validation

> **Status**: **MANDATORY** — Final repository state check  
> **Validation**: `check_protocol_compliance.py --clean`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Verify repository is in a clean, deployable state before ending session.

---

## Quick Checklist

- [ ] Verify on `main` branch (or ready to merge)
- [ ] Confirm `git status` shows clean working directory
- [ ] Verify synced with remote origin
- [ ] **Git Hygiene**: Delete merged local/remote branches and run `git fetch --prune`
- [ ] **Artifact Cleanup**: Delete temporary session files and obsolete artifacts
- [ ] **Orchestrator Check**: Run `check_protocol_compliance.py --clean`

---

## Detailed Requirements

### Repository State

- [ ] On `main` branch (or PR merged)
- [ ] Working directory clean (`git status`)
- [ ] Up to date with remote origin
- [ ] No uncommitted changes
- [ ] No unpushed commits
- [ ] Merged branches deleted (local and remote)

### Artifact Lifecycle Management

- [ ] Delete temporary files created during session (e.g., `task.md`, friction logs)
- [ ] If migration complete, remove obsolete `walkthrough.md` files
- [ ] Close browser tabs opened for testing
- [ ] Clear session locks if applicable
- [ ] Remove debug/test artifacts

---

## Verification Commands

```bash
# Check current branch
git branch --show-current

# Check for uncommitted changes
git status

# Check sync with remote
git fetch origin
git status
```

### Expected Output

```bash
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

## Orchestrator Validation

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --clean
```

**Verifies**:

- [ ] On main branch (or clean feature branch)
- [ ] Working directory clean
- [ ] Synced with remote origin

---

## Common Issues

| Issue | Solution |
| :--- | :--- |
| Uncommitted changes | `git add . && git commit -m "message"` |
| Behind remote | `git pull --rebase origin main` |
| On wrong branch | `git checkout main` or merge PR |
| Temp files present | Delete manually or add to `.gitignore` |

---

- [← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
