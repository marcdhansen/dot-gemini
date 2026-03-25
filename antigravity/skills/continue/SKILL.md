---
name: continue
description: Continue a session by reading the session handoff file and picking up where the previous agent left off
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# Continue Skill

Continue a session by reading the project handoff file and resuming work.

## Usage

```bash
/continue
```

## What It Does

1. Reads `.agent/handoffs/*-session.md` to get project context
2. Runs `git pull` to get latest code
3. Checks inbox for messages: `python3 src/agent_harness/scripts/poll_inbox.py`
4. Reports on current project state and priorities
5. Shows what the previous agent was working on

## Implementation

```bash
# Check for session handoff files
ls .agent/handoffs/*-session.md

# Read the most recent one
cat .agent/handoffs/agent-harness-session.md
```

## Response Format

```
📋 SESSION CONTINUE
==================
Project: [project-name]
Last session: [date]
Status: [active/complete/etc]

📊 Current State:
- [component]: [status]
- ...

🎯 Priorities:
1. [priority 1]
2. [priority 2]
...

📬 Pending Messages: [count]
...
```
