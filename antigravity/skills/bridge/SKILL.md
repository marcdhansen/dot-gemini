---
name: bridge
description: >
  Plan review between Claude and OpenCode agents. Use when submitting a
  plan for another agent to review, when two agents need to agree before
  proceeding, or when cross-agent negotiation is needed.
  Do NOT use for single-agent planning (use planning).
compatibility: >
  Requires the claude-bridge MCP server running locally. State and logs live
  in ~/Documents/claude-opencode-bridge/. Watcher process (Ollama llama3.2:3b)
  auto-starts at login and must be running for automated reviews.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: multi-agent
  tags: [negotiation, multi-agent, planning, cross-agent, mcp]
---

# Skill: bridge

**Purpose**: Multi-round negotiation protocol between Claude and OpenCode. Agents
review each other's plans, iterate with structured feedback, and reach agreement
before acting — or escalate to the human when stuck.

## Usage

```
/bridge                   # show bridge status
/bridge review            # review pending plans from the other agent  
/bridge post <title>      # post a plan, negotiate until approved
/bridge negotiate <id>    # resume an existing negotiation
```

## How It Works

1. Agent posts a plan with `post_plan`
2. Watcher (Ollama/llama3.2:3b, local, no API key) auto-reviews within ~15s
3. Review returns structured feedback: `must_fix[]` (blockers) + `nice_to_have[]`
4. If changes needed, agent calls `post_revision` with fixes (and optional counterproposals)
5. Repeat up to `max_revisions` (default 5) rounds
6. On approval → macOS notification + proceed
7. On deadlock/timeout/max → macOS notification + escalate to human

## MCP Tools (claude-bridge server)

| Tool | Args | Description |
|------|------|-------------|
| `post_plan` | agent, title, plan, max_revisions?, revision_timeout_hours? | Start a negotiation |
| `post_revision` | plan_id, agent, revised_plan, changes_made, disputed_items? | Submit revised plan |
| `get_reviews` | agent | Get review of your latest revision (REVIEW_READY or WAIT) |
| `get_negotiation` | plan_id | Full revision + review history |
| `get_pending` | agent | Other agent's revisions awaiting your review |
| `post_review` | plan_id, reviewer, feedback, approved, must_fix?, nice_to_have? | Submit manual review |
| `get_all` | — | Full state dump |

## Review Response Format

```
REVIEW_READY
Verdict: APPROVED | CHANGES_REQUESTED | DEADLOCKED | ESCALATED
Progress: high/medium/none (X/Y must-fix items resolved)
Must fix:
  - [item 1]
  - [item 2] (DISPUTED)
Nice to have:
  - suggestion
Feedback: <paragraph>
Action: PROCEED | address must-fix items and call post_revision | ESCALATED
```

## Files
- State:   `~/Documents/claude-opencode-bridge/bridge_state.json`
- Logs:    `~/Documents/claude-opencode-bridge/watcher.log`
- Watcher: `~/Documents/claude-opencode-bridge/watcher.py` (auto-starts at login)
