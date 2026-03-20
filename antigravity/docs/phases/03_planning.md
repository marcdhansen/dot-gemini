# Phase 3: Planning

> **Status**: **MANDATORY** for new features/significant changes  
> **Skill**: `/plan scope <task-id>`  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Define what will be built, how it will be verified, and get user approval before execution.

---

## Quick Checklist

- [ ] Create/update `implementation_plan.md` with proposed changes
- [ ] Perform blast radius analysis for significant changes
- [ ] Define milestones and success criteria
- [ ] Get user approval before proceeding to the Execution Phase
- [ ] **Create/Identify Beads Issue**: Mandatory before starting execution
- [ ] Update `task.md` with current objectives

---

## Detailed Requirements

### Blast Radius Analysis

Progressive disclosure levels:

| Level | When to Use | Includes |
| ------- | ------------- | ---------- |
| **Level 1 (Summary)** | Quick assessment | Risk level, affected files count, timeline impact |
| **Level 2 (Detailed)** | Development planning | Dependency chains, test coverage gaps, migration needs |
| **Level 3 (Deep-Dive)** | P0/P1 changes | Performance implications, security, long-term maintenance |

- [ ] **Level 1**: Quick overview with risk assessment
- [ ] **Level 2**: Module-level analysis if needed
- [ ] **Level 3**: Full architectural review for P0/P1

### Implementation Plan

- [ ] Create/update `implementation_plan.md`
- [ ] Document proposed changes by component
- [ ] Define verification plan (tests, manual validation)
- [ ] Identify rollback procedures

### Milestones

- [ ] Define success criteria for each phase
- [ ] Establish validation checkpoints
- [ ] Document A/B testing requirements if applicable

### Approval

> [!CAUTION]
> **Explicit Execution Approval Required**: Planning-to-Execution transition is BLOCKED until user provides explicit approval.

- [ ] Present plan to user for review
- [ ] Address feedback and update plan
- [ ] **Receive explicit approval** (e.g., "👍 APPROVED FOR EXECUTION")
- [ ] Record approval in `task.md` (Orchestrator looks for `## Approval` header or `[x]` markers)
- [ ] **Freshness Requirement**: Approval must be within the last 4 hours (validated via file modification time)

---

## Implementation Plan Template

```markdown
# [Goal Description]

Brief description of the problem and what the change accomplishes.

## User Review Required

> [!IMPORTANT]
> Document breaking changes or significant design decisions here.

## Proposed Changes

### [Component Name]

#### [MODIFY] [file.py](file:///path/to/file.py)
- Change description

#### [NEW] [new_file.py](file:///path/to/new_file.py)
- Purpose description

## Verification Plan

### Automated Tests
- Commands to run

### Manual Verification
- Steps to verify
```

---

## Planning Commands

```bash
# Scope selected task with blast radius analysis
/plan scope <task-id>

# Create implementation plan and milestones
/plan proceed <task-id>

# Quick blast radius analysis
/plan blast-radius <path>
```

---

*[← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
