# Phase 7: Clean State

> **Status**: **MANDATORY** — Final repository state check  
> **Validation**: `check_protocol_compliance.py --clean`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Verify repository is in a clean, deployable state before ending session.

---

## Quick Checklist

- [ ] On `main` branch (or PR merged)
- [ ] `git status` shows clean working directory
- [ ] Synced with remote origin
- [ ] Delete temporary session files (`task.md`, friction logs, etc.)
- [ ] Delete merged local/remote branches
- [ ] **Orchestrator Check**: `check_protocol_compliance.py --clean`

---

## Expected State

```bash
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

## Common Fixes

| Issue | Solution |
| :--- | :--- |
| Uncommitted changes | `git add . && git commit` |
| Behind remote | `git pull --rebase` |
| On wrong branch | `git checkout main` |
| Temp files | Delete manually |

---

*[← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
