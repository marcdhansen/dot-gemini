---
name: Orchestrator
description: Agent orchestrator that verifies SOP compliance at each phase (Initialization, Finalization). Validates that agents complete each step adequately and invoke appropriate skills at the right times.
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# Orchestrator Skill

The Orchestrator acts as an **agent supervisor**, verifying that each step of the Standard Operating Procedure (SOP) is completed adequately and that appropriate skills are invoked at the right times.

## Usage

```bash
# Initialization validation
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --init

# Finalization validation
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize

# Full orchestration status
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --status
```

## Purpose

Position as the **central orchestrator** that:

1. **Verifies SOP Compliance**: Checks that each Initialization and Finalization step is completed
2. **Validates Skill Invocation**: Ensures appropriate skills are used at each phase
3. **Gates Progression**: Blocks transitions if prerequisites aren't met
4. **Reports Status**: Provides clear pass/fail reporting for each checkpoint

## Orchestration Phases

### Phase 1: Initialization

```mermaid
graph TD
    A[Start Initialization] --> B{Tool Check}
    B -->|Pass| C{Context Check}
    B -->|Fail| X[BLOCKED]
    C -->|Pass| D{Issue Check}
    C -->|Fail| X
    D -->|Pass| E{Navigation Check}
    D -->|Fail| X
    E -->|Pass| F[✅ Initialization Complete]
    E -->|Fail| X
```

**Verifies**:

- [ ] Tools available (`bd`, `uv`, etc.)
- [ ] Planning documents readable
- [ ] Beads issue exists
- [ ] Plan approval fresh (< 4 hours)

### Phase 2: Execution Phase

**Passive Monitoring** - Orchestrator doesn't block during execution but logs:

- Task progress updates
- Significant decisions
- Skill invocations

### Phase 3: Finalization

```mermaid
graph TD
    A[Start Finalization] --> B{Quality Gates}
    B -->|Pass| C{Git Clean}
    B -->|Fail| X[BLOCKED]
    C -->|Pass| D{Reflect Invoked}
    C -->|Fail| X
    D -->|Pass| E{Retrospective Invoked}
    D -->|Fail| W[WARNING]
    E -->|Pass| F[✅ Finalization Complete]
    E -->|Fail| W
    W --> F
```

**Verifies**:

- [ ] Quality gates passed
- [ ] Git status clean
- [ ] Reflect skill invoked
- [ ] Retrospective skill invoked (warning if not)

## Skill Invocation Verification

Orchestrator verifies these skills are invoked at appropriate times:

| Phase | Skill | Required |
| :--- | :--- | :--- |
| Initialization | `initialization-briefing` | Recommended |
| Initialization | `devils-advocate` | Recommended for complex tasks |
| Finalization | `reflect` | **Required** |
| Finalization | `retrospective` | **Required** |

## Output Format

### Pass Example

```text
✅ INITIALIZATION COMPLETE
├── Tools: ✅ All required tools available
├── Context: ✅ Planning documents accessible  
├── Issues: ✅ Beads issue LIGHTRAG-123 assigned
└── Approval: ✅ Plan approved 2 hours ago

Ready to start!
```

### Fail Example

```text
❌ INITIALIZATION BLOCKED
├── Tools: ✅ All required tools available
├── Context: ❌ ImplementationPlan.md not found
├── Issues: ✅ Beads issue LIGHTRAG-123 assigned
└── Approval: ⚠️ Plan approval is 5 hours old (stale)

BLOCKERS:
1. Create implementation plan before proceeding
2. Re-approve plan (approval expires after 4 hours)
```

## Integration

The Orchestrator integrates with:

- **SOP Protocol**: Enforces Initialization/Execution/Finalization workflow
- **Beads**: Validates issue assignment and status
- **Skills**: Verifies skill invocation at each phase
- **Git**: Validates repository state

## Error Handling

If Orchestrator itself fails:

1. Check Python environment: `python3 --version`
2. Verify script exists: `ls ~/.gemini/antigravity/skills/Orchestrator/scripts/`
3. Check file permissions: `chmod +x check_protocol_compliance.py`
4. Run with verbose: `--verbose` flag for detailed output

## Configuration

Orchestrator reads configuration from:

- Project-level: `.agent/orchestrator.yaml`
- Global-level: `~/.gemini/antigravity/orchestrator.yaml`

### Config Options

```yaml
initialization:
  require_beads_issue: true
  plan_approval_hours: 4
  required_tools:
    - bd
    - git

finalization:
  require_reflection: true
  require_retrospective: true
  block_on_dirty_git: true
```
