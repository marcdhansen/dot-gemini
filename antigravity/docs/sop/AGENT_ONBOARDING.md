# 🚀 Agent Onboarding & Standard Protocols

To initialize an agent in a new environment or project, follow these universal steps:

## 1. Anchor to Global Memory

Identify global configuration directories to understand the system-wide rules.
> "Read the Global Standard Operating Procedure (SOP) in `~/.agent/docs/sop/SOP.md` and follow the standard protocols. Use the Global Index at `~/.agent/docs/GLOBAL_INDEX.md` as your primary navigation map."

## 2. Verify Tool Availability

Confirm the core toolchain is accessible. Common tools include:

```bash
which bd uv python git
```

## 3. Coordination & Multi-Agent Protocol

Most projects use an automated **session coordination system** to prevent conflicts on the same task.

### Step A: Initialize Session

Always look for a bootstrap or initialization script in the project root. Common scripts include:

- `agent-init.sh`
- `initialization.py`

These scripts typically:

1. **Tool Check**: Verifies required dependencies.
2. **Conflict Check**: Ensures no other agent is active on the same task.
3. **Registration**: Registers the current session in the task system.

### Step B: Operational Rules

- **Isolation**: Always work on a dedicated branch or worktree.
- **Cleanup**: Always run the designated finalization or cleanup procedures before ending a session.

## 4. Connect to Project Brain

Discover project-specific context by searching the workspace:

- `.agent/rules/ROADMAP.md`
- `.agent/rules/ImplementationPlan.md`
- `README.md`
- Running `bd ready` (if Beads is used)

## 5. Standard Development Workflow (Spec-Driven TDD)

All development should follow **spec-driven Test-Driven Development (TDD)**:

### A. Specification First

1. Read the specification in the workspace (e.g., `task.md` or `ImplementationPlan.md`).
2. Understand requirements completely.

### B. Test-Driven Development

1. Write failing tests first.
2. Confirm the failure.
3. Implement minimal code.
4. Refactor.

## 6. Standard Session Loop (Finalization)

Always execute the **Finalization** procedure before ending a session:

1. Run quality gates (linters, tests).
2. Update/Close tasks.
3. Sync and Push changes.

## 📚 Additional Documentation

Refer to the [GLOBAL_INDEX.md](~/.agent/docs/GLOBAL_INDEX.md) for deeper technical guides on the skills and command systems.
