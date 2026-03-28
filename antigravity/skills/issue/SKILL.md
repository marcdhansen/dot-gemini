---
name: issue
description: OpenClaw-powered beads issue management - get next task, check status, claim issues
allowed-tools: Bash, Read, Glob, Grep
---

# Issue Management Skill (OpenClaw-powered)

The `issue` skill uses OpenClaw to manage beads issues intelligently.

## Usage

```bash
/issue next     # Get next task recommendation
/issue status   # Check session/status
/issue init     # Initialize session (requires claimed issue)
/issue validate # Validate SOP compliance
/issue close    # Close session
/issue          # Default: run next
```

## Commands

### next (default)
Invokes OpenClaw to analyze available tasks and recommend what to work on next:
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh next
```

### status
Check current session state, in-progress tasks, git status, and SOP compliance:
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh status
```

### init
Initialize a new session for a specific issue:
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh init <issue-id>
```

### validate
Validate SOP compliance for current phase:
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh validate [phase]
```

### close
Close session, run quality gates, create handoff docs:
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh close
```

## Quick Beads Commands

- `bd ready` - Show available tasks
- `bd list` - Show in-progress tasks  
- `bd show <id>` - Show issue details
- `bd update <id> --claim` - Claim an issue
- `bd update <id> --close --reason "Done"` - Close issue

## Auto Mode (Recommended)

The auto wrapper provides automatic session management - OpenClaw becomes a real-time co-pilot:

```bash
# Start session with auto-claim
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/auto-issue.sh start --claim

# Signal phase transitions (OpenClaw validates and reminds)
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/auto-issue.sh phase execution

# Start background monitoring (watch mode)
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/auto-issue.sh watch

# End session (auto-finalize with quality gates)
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/auto-issue.sh end
```

### Auto Mode Workflow

1. **Session Start**: `auto-issue.sh start` checks `bd ready`, recommends task, optionally claims it
2. **Phase Transitions**: `auto-issue.sh phase <name>` runs OpenClaw validation, shows reminders
3. **Background Watch**: `auto-issue.sh watch` polls session state, alerts on phase changes
4. **Session End**: `auto-issue.sh end` runs quality gates, closes issue, creates handoff

### Phase Names

- `init` - Session initialization
- `planning` - Planning phase
- `execution` - Implementation (TDD reminder)
- `finalization` - Quality gates, PR
- `retrospective` - /reflect
- `clean` - Git cleanup

## Integration

- Uses OpenClaw for intelligent issue analysis
- Runs `bd ready` for task discovery
- Provides specific commands to claim and manage tasks
- Validates SOP compliance at each phase
- Auto mode reduces manual orchestrator commands