---
name: continue
description: >
  Resume a previous agent session by loading its handoff artifact. Scans
  ~/.agent/handoff/ for recent handoffs, presents a summary of open work,
  blockers, and next recommended action, then primes working memory for the
  new session. Use at session start when continuing interrupted or
  handed-off work.
  Do NOT use when starting fresh work with no prior session to resume.
compatibility: >
  Requires Read access to ~/.agent/handoff/. Script at
  ~/.agent/skills/continue/scripts/continue.py.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: session-management
  tags: [handoff, session-resume, continuity, working-memory]
  allowed-tools: Bash, Read
---

# Skill: /continue

**Purpose**: Discover and load a prior session handoff so a new agent can resume
work without losing context.

---

## Usage

```bash
/continue                                    # auto-load most recent handoff
/continue opencode                           # most recent from a specific agent
/continue opencode-20260314T150423-a3f7      # exact session by ID
```

Or run the script directly:

```bash
python ~/.agent/skills/continue/scripts/continue.py [id_or_agent]
```

---

## What it does

1. Scans `~/.agent/handoff/` for handoff files matching the request
2. Presents a structured summary: Done / Open / Blockers / Next recommended
3. Surfaces blockers explicitly — agent must not proceed past them without user sign-off
4. Primes working memory for Phase 1 of the new session

---

## Output example

```
━━━ Handoff: opencode-20260314T150423-a3f7 ━━━
Agent: opencode  |  2026-03-14T15:04:23
Task: Implement handoff protocol across ~/.agent/

✅ Done (5):
  • Created docs/sop/HANDOFF.md (schema v1.2, concurrent-safe)
  • Created skills/continue/ with continue.py and cleanup_handoffs.py
  • Patched AGENTS.md, SOP checklist, Phase 1 & 6, DAILY_START
  • Wired cleanup into agent-end.sh global hook
  • Documented project agent-end.sh → global hook requirement in COLLABORATION.md

🔄 Open (0):

🚫 Blockers:
  • None

➡️  Next: Add ~/.agent to filesystem MCP server allowed directories in
          ~/Library/Application Support/Claude/claude_desktop_config.json
          then restart Claude Desktop to eliminate write-via-bridge workaround
```

---

## When is a handoff written?

| Trigger | Who writes it | Notes |
|---------|--------------|-------|
| Context window ~75% full | Agent, proactively | Agent announces ID to user; does NOT wait to be asked |
| Normal session end | Agent, Phase 6 SOP | Part of Retrospective checklist |
| User says "wrap up" / "start fresh" | Agent, on cue | Writes before ending |

The writing agent always tells the user:
> "Handoff written: `{session-id}`. In your next session, type `/continue` to
> auto-resume, or `/continue {session-id}` for this exact session."

---

## Handoff file location and naming

```
~/.agent/handoff/{agent}-{YYYYMMDDTHHMMSS}-{4hex}.json
e.g.  opencode-20260314T150423-a3f7.json
      gemini-20260314T151102-c91e.json
```

`/continue` with no args loads the most recently modified file across all agents.

---

## See also

- **[HANDOFF.md](../../docs/sop/HANDOFF.md)** — full protocol spec and schema
- **[context-management](../context-management/SKILL.md)** — proactive handoff trigger at 75%
- **[cleanup_handoffs.py](scripts/cleanup_handoffs.py)** — prune old handoffs
- **[~/.agent/scripts/agent-end.sh](../../scripts/agent-end.sh)** — global session-end hook; project `./scripts/agent-end.sh` scripts must `source` this — see [COLLABORATION.md](../../docs/sop/COLLABORATION.md#session-management)
