---
description: Interact with the Claude-OpenCode review bridge — post plans, check reviews, inspect negotiations
---

# /bridge $ARGUMENT

Read `~/Documents/claude-opencode-bridge/bridge_state.json` then act.

## Tiers
| Tier   | Model                | Speed  | Use for                        |
|--------|----------------------|--------|--------------------------------|
| light  | llama3.2:3b          | ~10s   | Quick iterations               |
| medium | qwen2.5-coder:7b     | ~30s   | Code-heavy plans               |
| heavy  | mistral-nemo (12B)   | ~60s   | Architecture, security ← DEFAULT |
| ultra  | Claude Code CLI      | ~15s   | Highest quality, uses Claude.ai |

Auto-escalation: deadlock at one tier → automatically retries at next tier up.

---

## /bridge  or  /bridge status
Show:
- Watcher running? (`ps aux | grep watcher.py | grep -v grep`)
- Your negotiations: id, title, tier, status, revision count
- Plans from Claude pending your review

## /bridge post <title> [tier]
Post a plan and negotiate until approved. Tier defaults to `heavy`.

Examples:
  /bridge post Add OAuth login
  /bridge post Refactor database layer medium
  /bridge post Deploy payment service ultra

Steps:
1. `post_plan(agent="opencode", title="<title>", plan="<steps>", review_tier="<tier>")`
2. Wait 20s → `get_reviews(agent="opencode")`
3. **APPROVED** → proceed, stop calling get_reviews
4. **CHANGES_REQUESTED** → address must_fix → `post_revision(plan_id, agent, revised_plan, changes_made)` → wait 20s → `get_reviews`
5. **WAIT** → wait 20s, retry (max 20 times)
6. **DEADLOCKED** → watcher auto-escalates to next tier and re-reviews
7. **ESCALATED** → all tiers exhausted, notify user

## /bridge pending  or  /bridge review
Review plans Claude has posted:
`get_pending(agent="opencode")` → for each:
`post_review(plan_id, reviewer="opencode", feedback, approved, must_fix=[], nice_to_have=[])`

## /bridge history <plan_id>
`get_negotiation(plan_id)` — full revision + review history with tier used per review
