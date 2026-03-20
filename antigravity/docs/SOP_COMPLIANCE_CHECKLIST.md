# 📋 Standard Operating Procedure (SOP) Compliance Checklist

> **Purpose**: Universal checklist ensuring agents complete all required SOP phases.  
> **Audience**: AI agents and human developers.  
> **Source of Truth**: This document defines the authoritative workflow that the [Orchestrator](#-orchestrator-role) validates.

---

## ⚡ Mode Detection

> **Default**: Turbo Mode
> **Escalation Trigger**: ANY code change, Beads implementation, deep research, or explicit user request.

| Feature | Turbo Mode (Default) | Full Mode (Escalation) |
| :--- | :--- | :--- |
| **Use Case** | Issues, Q&A, minor doc edits | Implementation, research |
| **Briefing** | Truncated/Skip | Complete 7-phase SOP |
| **Initial Context** | Brief mental context | Mandatory Phase 1 & 2 |
| **Planning** | Optional | Mandatory Phase 3 |
| **Execution** | Direct action | Mandatory Phase 4 (TDD) |
| **Finalization** | Git sync only | Mandatory Phase 5 (Gates) |
| **Retrospective** | Optional/Brief | Mandatory Phase 6 |

---

## ⚡ Quick Reference Checklist

Use this summary for quick compliance verification. Click phase headers for detailed requirements.

### [Phase 1: Session Context](phases/01_session_context.md) — MANDATORY

- [ ] Review previous session context (what was done, what's pending)
- [ ] Create friction log for real-time capture
- [ ] Note friction areas to watch from past sessions
- [ ] Set mental context for upcoming work

### [Phase 2: Initialization](phases/02_initialization.md) — MANDATORY

- [ ] **Tool Check**: Verify required tools (`bd`, `uv`, `git`)
- [ ] **Context Check**: Read `ROADMAP.md` and `ImplementationPlan.md`
- [ ] **Status Check**: Run `bd ready` to see active tasks
- [ ] **Issue Check**: Run `bd ready` (Highly Recommended, optional for planning)
- [ ] **Plan Approval**: Confirm plan approved within 4 hours
- [ ] **🔒 Implementation Readiness**: **MANDATORY** validation before starting work
  - [ ] Beads Issue Exists (MANDATORY for implementation)
  - [ ] Feature Branch Active (true/false)
  - [ ] Baseline Performance Documented (true/false)
  - [ ] TDD Requirements Prepared (true/false)
  - [ ] Performance Assertions Defined (true/false)
  - **BLOCKING**: Any "false" → **WORK BLOCKED**
- [ ] **Orchestrator**: Run `check_protocol_compliance.py --init`

### [Phase 3: Planning](phases/03_planning.md) — MANDATORY

- [ ] Create/update `implementation_plan.md` with proposed changes
- [ ] Perform blast radius analysis for significant changes
- [ ] Define milestones and success criteria
- [ ] **Get explicit user approval before EXECUTION** (e.g., "👍 APPROVED FOR EXECUTION")
- [ ] Update `task.md` with current objectives

### [Phase 4: Execution](phases/04_execution.md)

- [ ] Keep `task.md` updated as living document
- [ ] **🔒 SOP Infrastructure Changes**: Code changes to Orchestrator scripts, skill scripts, SKILL.md files, or SOP docs **automatically trigger Full Mode** (Turbo Mode blocked)
- [ ] **🔒 Follow Mandatory Global TDD Workflow** - **[Global TDD Workflow](sop/tdd-workflow.md)**
  - [ ] **Specification Phase**: Define requirements and success criteria in planning docs
  - [ ] **🔴 Red Phase**: Create failing tests that define expectations
  - [ ] **🟢 Green Phase**: Write minimum code to make tests pass
  - [ ] **✅ Verification Phase**: Run tests and confirm they PASS
  - [ ] **🔄 Refactor Phase**: Clean up code while keeping tests passing
  - [ ] **📊 Audit Phase**: Document performance impacts and tradeoffs
- [ ] **🔒 Performance Requirements** (MANDATORY from global TDD)
  - [ ] **Baseline Measurements**: Document current system performance
  - [ ] **Performance Assertions**: Define measurable speed/memory/scalability requirements
  - [ ] **Benchmark Tests**: Create tests that validate performance claims
  - [ ] **Tradeoff Analysis**: Document speed vs resource vs accuracy tradeoffs
- [ ] Record significant decisions in planning docs
- [ ] Capture friction points in real-time
- [ ] For UI changes: test with browser/Playwright

### [Phase 5: Finalization](phases/05_finalization.md) — MANDATORY

- [ ] **Quality Gates**: Run linters, tests, pre-commit hooks
- [ ] **🔒 Atomic Commit Validation**: **MANDATORY** git history hygiene
  - [ ] Squash feature branch into single atomic commit
  - [ ] Ensure commit message follows conventions
  - [ ] Verify clean linear history against target branch
- [ ] **🔒 TDD Compliance Validation** (MANDATORY from global TDD)
  - [ ] **Failing Tests Before Implementation**: Confirm RED phase evidence
  - [ ] **Passing Tests After Implementation**: Confirm GREEN phase success
  - [ ] **Performance Benchmarks**: All performance assertions PASS
  - [ ] **Baseline Comparisons**: Document performance changes
  - [ ] **Tradeoff Documentation**: Complete speed-accuracy analysis
  - [ ] **Measurable Metrics**: All claims quantified
  - **BLOCKING**: Missing artifacts → **SESSION INCOMPLETE**
- [ ] **Markdown Check**: Run `markdownlint` on modified `.md` files
- [ ] **Git Sync**: Commit all changes, push to remote
- [ ] **🔒 PR Creation**: **MANDATORY** for code changes. Create a PR for the feature branch.
- [ ] **🔒 PR Review Issue**: Create P0 beads issue for PR review (Full Mode only)
  - [ ] Include PR link in issue
  - [ ] Invoke `/code-review` skill
  - **BLOCKING**: PR merge blocked until review issue closed
- [ ] **🔒 PR Rejection Response**: If PR received `REQUEST_CHANGES`:
  - [ ] Classify feedback (minor fix / rework / decomposition)
  - [ ] If decomposition requested: close original PR, create Epic/parent issue, create child issues, create focused child PRs
  - [ ] If ≥2 rejections: decomposition is MANDATORY
  - [ ] Reference: [PR Response Protocol](sop/pr-response-protocol.md)
  - **BLOCKING**: Thrashing guard violation (≥2 rejections without decomposition) → **WORK BLOCKED**
- [ ] **Beads Update**: Update/close issues appropriately
- [ ] **Closure Notes**: Add implementation details to closed issues (using `bd comments add <issue-id> "note"`)
- [ ] **Orchestrator**: Run `check_protocol_compliance.py --finalize`

### [Phase 6: Retrospective (Retrospective)](phases/06_retrospective.md) — MANDATORY

- [ ] **Reflect**: **MANDATORY** Generate `.reflection_input.json` with structured learnings using `/reflect`
- [ ] **Harness Review**: Evaluate protocol effectiveness using RBT analysis
- [ ] **Memory Sync**: Persist learnings to AutoMem/OpenViking
- [ ] **Handoff**: Summarize work, including **PR link**, issues created / closed, next steps
- [ ] **Protocol Compliance**: Verify and summarize SOP compliance status (validated via Orchestrator)
- [ ] **Plan Cleanup**: Clear approval marker in `task.md`
- [ ] **Strategic Analysis**: Address cognitive load, patterns, improvements, emergent methods
- [ ] **Orchestrator**: Run `check_protocol_compliance.py --retrospective`

### [Phase 7: Clean State Validation (Clean State)](phases/07_clean_state.md) — MANDATORY

- [ ] Verify on `main` branch (or ready to merge)
- [ ] Confirm `git status` shows clean working directory
- [ ] Verify synced with remote origin
- [ ] **Orchestrator**: Run `check_protocol_compliance.py --clean`

---

## 🏗️ LangGraph Harness (v2.0)

The SOP is now powered by a **LangGraph-native** orchestration engine. The harness replaces static markdown checklists with a dynamic, persistent workflow.

### Key Features

| Feature | Benefit |
| --- | --- |
| **Durable Checkpointing** | Resume from any failure point |
| **Human-in-Loop Gates** | `interrupt_before` for approvals |
| **Multi-Agent Delegation** | Sisyphus → Hephaestus → Oracle |
| **State Persistence** | SQLite-backed session state |

### Programmatic Usage

```python
from harness.engine import run_harness
run_harness("SESSION-001", "Execution phase", "thread-abc")
```

→ **Full Documentation**: [HARNESS_ARCHITECTURE.md](architecture/HARNESS_ARCHITECTURE.md)

---

## 🤖 Orchestrator Role

The **Orchestrator** is the central component that validates SOP compliance at each phase.

### Purpose

- **Verifies SOP Compliance**: Checks that each phase is completed
- **Validates Skill Invocation**: Ensures appropriate skills are used
- **Gates Progression**: Blocks transitions if prerequisites aren't met
- **Reports Status**: Provides clear pass/fail reporting

### Commands

```bash
# Initialization validation
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --init

# Finalization validation
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize

# Retrospective validation
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --retrospective

# Clean state verification
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --clean

# Full status overview
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --status
```

### Blocking vs. Warning

| Check | Failure Type |
| ----- | ------------ |
| Tools available | **BLOCKER** |
| Planning docs accessible | **BLOCKER** |
| Beads issue exists | **BLOCKER** (for Execution) |
| Plan approval fresh (<4h) | **BLOCKER** |
| Implementation Readiness (ALL checks) | **BLOCKER** |
| Global TDD Workflow compliance | **BLOCKER** |
| Performance Requirements (ALL checks) | **BLOCKER** |
| TDD Completion Artifacts (ALL artifacts) | **BLOCKER** |
| Quality gates passed | **BLOCKER** |
| Git status clean | **BLOCKER** |
| PR created for code changes | **BLOCKER** |
| PR link in handoff | **BLOCKER** |
| PR created for code changes | **BLOCKER** |
| PR link in handoff | **BLOCKER** |
| PR Review Issue exists | **BLOCKER** (for Full Mode) |
| Session context established | **BLOCKER** |
| Reflect invoked (.reflection_input.json) | **BLOCKER** |
| Retrospective completed | **BLOCKER** |

**🔒 New Mandatory TDD Enforcement**:

- **Implementation Readiness**: Any false → **WORK BLOCKED**
- **Global TDD Workflow**: Deviations → **WORK BLOCKED**
- **Performance Requirements**: Missing assertions → **WORK BLOCKED**
- **TDD Completion Artifacts**: Missing evidence → **SESSION INCOMPLETE**

---

## 📊 Phase Summary

```mermaid
graph LR
    A[Session Context] --> B[Initialization]
    B --> C[Planning]
    C --> D[Execution]
    D --> E[Finalization]
    E --> F[Retrospective]
    F --> G[Clean State]
    
    style A fill:#4dabf7,color:#fff
    style B fill:#4dabf7,color:#fff
    style C fill:#4dabf7,color:#fff
    style E fill:#4dabf7,color:#fff
    style F fill:#4dabf7,color:#fff
    style G fill:#4dabf7,color:#fff
```

**Legend**: Blue phases are **MANDATORY** and validated by the Orchestrator.

---

## 🔗 Related Documentation

| Document | Purpose |
| ---------- | --------- |
| [AGENTS.md](../AGENTS.md) | Universal agent protocols |
| [GLOBAL_INDEX.md](GLOBAL_INDEX.md) | Master documentation index |
| [🔒 Global TDD Workflow](sop/tdd-workflow.md) | **MANDATORY** TDD with enforcement (no bypass) |
| [Global Agent Rules](sop/GEMINI.md) | Global SOP procedures including TDD |
| [Orchestrator implementation](~/.gemini/antigravity/skills/Orchestrator/SKILL.md) | Logic behind the compliance checks |

---

---

*Last Updated: 2026-02-06*  
*Version: 3.1.0*  
*Major Update: Integrated mandatory global TDD enforcement with performance requirements and quality gates*
