# 📋 SOP Compliance Checklist

> **Source of Truth** for Full Mode SOP validation  
> **Audience**: AI agents and human developers  
> **Validation**: Orchestrator checks compliance at each phase

---

## ⚡ Mode Detection

| Feature | Turbo Mode (Default) | Full Mode (Escalation) |
| :--- | :--- | :--- |
| **Use Case** | Issues, Q&A, minor doc edits | Implementation, research |
| **Briefing** | Truncated/Skip | Complete 7-phase SOP |
| **Finalization** | Git sync only | Quality gates, PR, `/reflect` |

**Escalation Triggers**: Any code change, Beads task, deep research, user request.

---

## ⚡ Quick Reference Checklist

### [Phase 1: Session Context](phases/01_session_context.md) — MANDATORY

- [ ] Review previous session context (what was done, what's pending)
- [ ] Create friction log for real-time capture
- [ ] Note friction areas to watch from past sessions

### [Phase 2: Initialization](phases/02_initialization.md) — MANDATORY

- [ ] **Tool Check**: Verify required tools (`bd`, `git`)
- [ ] **Status Check**: Run `bd ready` to see active tasks
- [ ] **Plan Approval**: Confirm plan approved within 4 hours
- [ ] **🔒 Beads Issue**: **MANDATORY** for implementation (optional for planning)
- [ ] **Orchestrator**: `check_protocol_compliance.py --init`

### [Phase 3: Planning](phases/03_planning.md) — MANDATORY

- [ ] Create/update `implementation_plan.md`
- [ ] Perform blast radius analysis
- [ ] **⚠️ BLOCKING**: Get explicit approval (`👍 APPROVED FOR EXECUTION`) before execution
- [ ] Update `task.md` with current objectives

### [Phase 4: Execution](docs/sop/tdd-workflow.md) — TDD REQUIRED

- [ ] Keep `task.md` updated
- [ ] **Follow Spec-Driven TDD**: Red → Green → Refactor
- [ ] Capture friction points in real-time

### [Phase 5: Finalization](phases/05_finalization.md) — MANDATORY

- [ ] **Quality Gates**: Run linters, tests, pre-commit hooks
- [ ] **Git Sync**: Commit all changes, squash into atomic commit
- [ ] **🔒 PR Creation**: **MANDATORY** for code changes
- [ ] **Beads Update**: Update/close issues
- [ ] **Orchestrator**: `check_protocol_compliance.py --finalize`

### [Phase 6: Retrospective](phases/06_retrospective.md) — MANDATORY

- [ ] **Reflect**: Run `/reflect` to generate `.reflection_input.json`
- [ ] **Memory Sync**: Persist learnings to AutoMem/OpenViking
- [ ] **Handoff**: Include PR link, issues created/closed, next steps
- [ ] **Plan Cleanup**: Clear approval marker in `task.md`

### [Phase 7: Clean State](phases/07_clean_state.md) — MANDATORY

- [ ] Verify on `main` branch (or ready to merge)
- [ ] Confirm `git status` shows clean working directory
- [ ] Delete temporary session files
- [ ] **Orchestrator**: `check_protocol_compliance.py --clean`

---

## 🔒 Blocking Rules

| Check | Failure Type |
| ----- | ------------ |
| Beads issue exists | **BLOCKER** (for Execution) |
| Plan approval fresh (<4h) | **BLOCKER** |
| Quality gates passed | **BLOCKER** |
| Git status clean | **BLOCKER** |
| PR created for code changes | **BLOCKER** |
| Reflect invoked | **BLOCKER** |

---

## 📊 Phase Summary

```
Session Context → Initialization → Planning → Execution → Finalization → Retrospective → Clean State
      ↓                ↓              ↓           ↓            ↓               ↓            ↓
   Mental         Tools/Docs      Approval    TDD Work     Quality         Reflect       Clean
   Context        Verified        Required    Required     Gates           Required      State
```

**Legend**: All phases except Execution are **MANDATORY**.

---

## 🔗 Related Documentation

| Document | Purpose |
| ---------- | --------- |
| [SOP.md](sop/SOP.md) | Global Agent Rules & Procedures |
| [TDD Workflow](sop/tdd-workflow.md) | Mandatory TDD with enforcement |
| [COLLABORATION.md](sop/COLLABORATION.md) | Multi-agent coordination |
| [BEADS_GUIDE.md](BEADS_GUIDE.md) | Task management |
| [Orchestrator Skill](../skills/Orchestrator/SKILL.md) | Compliance validation logic |

---

*Last Updated: 2026-03-19*  
*Version: 4.0.0*  
*Major Update: Progressive disclosure - expanded details in phase files*
