# Phase 6: Retrospective

> **Status**: **MANDATORY** — Strategic learning after finalization  
> **Skill**: `/reflect`  
> **Validation**: `check_protocol_compliance.py --retrospective`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Capture strategic learnings, provide handoff summary, and ensure continuous improvement.

---

## ⚠️ CRITICAL: Reflect Required

> **Run `/reflect` to generate `.reflection_input.json`**  
> This is BLOCKING — session cannot complete without it.

---

## Quick Checklist

- [ ] **Reflect**: Run `/reflect` to generate `.reflection_input.json`
- [ ] **Memory Sync**: Persist learnings to AutoMem/OpenViking
- [ ] **Handoff**: Include PR link, issues created/closed, next steps
- [ ] **Plan Cleanup**: Clear approval marker in `task.md`
- [ ] **Orchestrator Check**: `check_protocol_compliance.py --retrospective`

---

## Handoff Summary

Provide clear summary including:

- [ ] Work completed and deliverables
- [ ] **PR Link**: Link to GitHub Pull Request
- [ ] Beads issues created/closed (specific IDs)
- [ ] Recommended next steps

### Session Closure Document

The **session handoff document** in `.agent/handoffs/` is the single source of truth for session closure. This consolidates what was previously split between debrief.md and handoff documents.

- **Location**: `.agent/handoffs/{branch-name}-session.md`
- **Contents**: Work summary, issues, next steps, PR links
- **Replaces**: debrief.md (deprecated)

### Strategic Questions

Address these during reflection:

| Question | Focus Areas |
| --- | --- |
| **Cognitive Load** | Can manual SOP steps be automated? |
| **Design Patterns** | What patterns should be formalized? |
| **Emergent Methods** | Better approaches discovered during session? |

### RBT Analysis

- [ ] **Roses** (🌹): What worked well?
- [ ] **Buds** (🌱): What could be improved?
- [ ] **Thorns** (🌿): What failed repeatedly?

---

## Orchestrator Validation

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --retrospective
```

---

*[← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
