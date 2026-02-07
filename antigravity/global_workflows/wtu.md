---
description: wrap this session up
---

# 🏁 Session Wrap-Up Workflow

Run Phases 5-7 of the SOP to properly close out the session.

---

## Phase 5: Finalization

Run quality gates, commit changes, and sync with remote:

```bash
~/.gemini/antigravity/skills/finalization/scripts/finalization.sh
```

Then validate:

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize
```

---

## Phase 6: Retrospective

Capture learnings and provide handoff summary:

```bash
/reflect
```

Then validate:

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --retrospective
```

---

## Phase 7: Clean State

Verify repository is clean and ready for next session:

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --clean
```

All checks should pass before ending the session.
