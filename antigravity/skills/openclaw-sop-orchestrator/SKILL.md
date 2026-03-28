---
name: openclaw-sop-orchestrator
description: OpenClaw-based SOP orchestrator that handles session initialization, task management, and compliance validation using intelligent agentic workflows.
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# OpenClaw SOP Orchestrator Skill

This skill invokes OpenClaw to handle SOP orchestration tasks intelligently, replacing the static Python check_protocol_compliance.py with an intelligent agent.

## Invocation

```bash
/openclaw-sop-orchestrator
```

Or via opencode skill invocation when user asks "what should I work on next?"

## What It Does

1. **Task Discovery**: Invokes OpenClaw to run `bd ready` and analyze available tasks
2. **Intelligent Recommendations**: Uses OpenClaw's agentic capabilities to provide contextual task recommendations
3. **Session Management**: Can initialize sessions, claim tasks, and update beads issues
4. **SOP Compliance**: Validates that agents follow the 7-phase SOP workflow

## Implementation

The skill executes the orchestration script:

```bash
# Invoke via the script
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh next

# Or directly with OpenClaw
cd ~/GitHub/marcdhansen/openclaw
OLLAMA_API_KEY="ollama-local" npx openclaw agent --agent main --message "Run SOP initialization check..." --timeout 120 --local
```

## Commands

- `orchestrate.sh next` - Get next task recommendation
- `orchestrate.sh init <issue-id>` - Initialize session
- `orchestrate.sh validate [phase]` - Validate SOP compliance
- `orchestrate.sh close` - Close session
- `orchestrate.sh status` - Show session status

## Why OpenClaw?

- **Intelligent**: Can make contextual decisions beyond static checks
- **Dogfooding**: Uses our own tool for SOP orchestration
- **Adaptive**: Can handle edge cases that Python scripts can't
- **Tool-capable**: Can directly interact with beads, git, and other tools

## Integration Points

### Phase 1: Light Touch
- `/next` command triggers OpenClaw for task recommendations
- Validates the approach before full integration

### Full Integration
- Replace check_protocol_compliance.py calls with OpenClaw invocations
- OpenClaw handles:
  - Session initialization checks
  - SOP compliance validation at each phase
  - Finalization checks
  - Quality gates invocation
  - Issue creation/updates via bd

## Error Handling

If OpenClaw invocation fails:
1. Fall back to direct `bd ready` command
2. Show available tasks without intelligent recommendations
3. Log the error for debugging

## Configuration

Requires:
- OpenClaw installed at ~/GitHub/marcdhansen/openclaw
- Ollama running with a tool-capable model (qwen2.5:0.5b or larger)
- beads (bd) CLI installed and configured
