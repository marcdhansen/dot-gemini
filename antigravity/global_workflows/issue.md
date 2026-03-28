---
description: Manage beads issues - get next task, check status, claim issues
---

Use this workflow for beads issue management. Options:

**Get next task recommendation:**
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh next
```

**Check session/status:**
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh status
```

**Initialize session with issue:**
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh init <issue-id>
```

**Validate SOP compliance:**
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh validate [phase]
```

**Close session:**
```bash
~/.config/opencode/skills/openclaw-sop-orchestrator/scripts/orchestrate.sh close
```

**Quick beads commands:**
- `bd ready` - Show available tasks
- `bd list` - Show in-progress tasks
- `bd show <id>` - Show issue details
- `bd update <id> --claim` - Claim an issue