# Phase 4: Execution

> **Status**: Ongoing during active development  
> **Monitoring**: Orchestrator passively logs progress  
> **Back to**: [SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)

---

## Purpose

Execute the approved plan while maintaining quality practices and documentation.

---

## Quick Checklist

- [ ] Keep `task.md` updated as living document
- [ ] Follow Spec-Driven TDD (Red → Green → Refactor)
- [ ] Record significant decisions in planning docs
- [ ] **Progress Logging**: Append structured entries to `{issue-id}.md`
- [ ] Capture friction points in real-time
- [ ] For UI changes: test with browser/Playwright

---

## Detailed Requirements

### Task Management

- [ ] Keep `task.md` updated with progress
- [ ] Mark items as `[/]` when in progress
- [ ] Mark items as `[x]` when completed

### Spec-Driven TDD

| Phase | Description |
| :--- | :--- |
| **Red** | Write failing test first |
| **Green** | Implement minimum code to pass |
| **Refactor** | Improve while keeping tests green |

- [ ] **Red Phase**: Write failing test first
- [ ] **Green Phase**: Implement minimum code to pass
- [ ] **Refactor**: Improve while keeping tests green

### Decision Recording

- [ ] Document significant decisions in planning docs
- [ ] Record rationale for architectural choices
- [ ] Note deviations from plan with justification

### Progress Logging (MANDATORY)

- [ ] Create progress log entry after each significant milestone
- [ ] Include reflector insights (what worked, what failed)
- [ ] Use `/log-progress` to automate formatting and auto-commit

### Quality Practices

- [ ] Run tests after each significant change
- [ ] For UI changes: Test with browser/Playwright
- [ ] Capture friction points in real-time (not retrospectively)

### Course Correction

- [ ] If plan needs to change, switch to PLANNING mode
- [ ] Update artifacts before continuing execution
- [ ] Get re-approval for significant deviations

### Multi-Agent Delegation (Sisyphus Team)

The LangGraph harness supports multi-agent orchestration during execution:

| Agent | Role | Invoked For |
| :--- | :--- | :--- |
| **Sisyphus** | Lead Orchestrator | Complex multi-step tasks |
| **Hephaestus** | Code Implementation | Writing, linting code |
| **Oracle** | Validation | Testing, verification |

The harness automatically delegates to specialists via subgraphs. See [HARNESS_ARCHITECTURE.md](../architecture/HARNESS_ARCHITECTURE.md).

---

## Value-Driven Complexity Scaling

Start simple, add complexity only after value is demonstrated:

```markdown
Simple modification → Demonstrate value → Complex implementation
```

**Rules**:

- Prefer simple modifications for new features
- Only proceed to complex implementations after value proven
- Document rationale for complexity increases

---

## Container Management

If containers are needed:

- Run Docker without Docker Desktop (use CLI alternatives like OrbStack/Colima)
- Minimize resource consumption

---

- [← Back to SOP Checklist](../SOP_COMPLIANCE_CHECKLIST.md)*
