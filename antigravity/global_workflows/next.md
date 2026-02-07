---
description: Start a new session with Phase I (Session Context) then show available tasks
---

# 🚀 Session Start Workflow

This workflow properly follows SOP by running Phase I (Session Context) before Phase II (Task Discovery).

## Phase I: Session Context

Run the initialization briefing for mental preparation and friction awareness:

```bash
python ~/.gemini/antigravity/skills/initialization-briefing/initialization_briefing.py
```

## Phase II: Task Discovery

Show available tasks to work on:

```bash
uv run scripts/show_next_tasks.py
```

After running both phases, provide your thoughts on which issues to work on next.
