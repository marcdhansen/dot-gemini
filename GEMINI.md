# 🌟 Gemini Agent Configuration

**Scope**: PROVIDER-SPECIFIC — Gemini CLI and Antigravity only.

> [!IMPORTANT]
> Universal SOP lives in `~/.agent/AGENTS.md` — read that first.
> This file contains ONLY what is specific to Gemini and Antigravity.

---

## 🚀 Session Initialization

After running `~/.agent/bin/agent-session-gate` (from AGENTS.md), run:

```bash
export AGENT_PROVIDER=gemini
python ~/.gemini/antigravity/skills/initialization-briefing/initialization_briefing.py --turbo
```

---

## 🔧 Gemini-Specific Configuration

| File | Purpose |
|:-----|:--------|
| `~/.gemini/GEMINI.md` | This file — Gemini/Antigravity provider config |
| `~/.gemini/settings.json` | Gemini CLI settings (includeDirectories, sandbox, etc.) |
| `~/.gemini/antigravity/global_workflows/` | Slash commands (also `~/.claude/commands/`) |
| `~/.gemini/antigravity/skills/` | Canonical skill source (all agents symlink here) |
| `~/.gemini/antigravity/brain/` | Project planning state (Antigravity-managed) |

---

## 🧬 Gemini-Specific Memories

- **Brain/Planning**: `~/.gemini/antigravity/brain/PROJECT_ID/`
- **Global Workflows**: `~/.gemini/antigravity/global_workflows/`
- `/memory show` — inspect full context currently loaded
- `/memory refresh` — reload after manual edits
- `/memory add <text>` — write to this file permanently

---

## 📚 Navigation

→ **Universal Protocol**: `~/.agent/AGENTS.md`
→ **Master Index**: `~/.agent/docs/GLOBAL_INDEX.md`
