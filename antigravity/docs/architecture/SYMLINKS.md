# 🔗 Complete Symlink Ecosystem Reference

**Purpose**: Comprehensive technical reference for symlink architecture.
**Last Updated**: 2026-03-22

---

## 🏗️ Core Principle: Antigravity as Universal Source

Skills and commands physically live in `~/.gemini/antigravity/` because
**Antigravity IDE cannot follow symlinks**. All other agents work around this
by symlinking TO antigravity rather than FROM it.

This is a workaround, not a design choice. When Antigravity gains symlink
support, the direction will reverse (antigravity → ~/.agent/).

---

## 🌐 Complete Symlink Map

### Skills
```
~/.gemini/antigravity/skills/           ← ACTUAL DIRECTORY (Antigravity constraint)
~/.agent/skills/                     → ~/.gemini/antigravity/skills/
~/.claude/skills/                    → ~/.gemini/antigravity/skills/
~/.config/opencode/skills/           → ~/.gemini/antigravity/skills/
```

### Commands / Workflows
```
~/.gemini/antigravity/global_workflows/ ← ACTUAL DIRECTORY
~/.gemini/antigravity/commands/      → global_workflows/  (internal)
~/.agent/commands/                   → ~/.gemini/antigravity/global_workflows/
~/.claude/commands/                  → ~/.gemini/antigravity/global_workflows/
~/.config/opencode/commands/         → ~/.gemini/antigravity/global_workflows/
```

### Instructions (single source of truth)
```
~/.agent/AGENTS.md                   ← ACTUAL FILE
~/.claude/CLAUDE.md                  → ~/.agent/AGENTS.md
~/.config/opencode/AGENTS.md        → ~/.agent/AGENTS.md
```

---

## 📋 Setup

Run `~/dot/setup.sh` to create all symlinks above.

Verify with:
```bash
ls -la ~/.claude ~/.agent ~/.config/opencode
```

---

## 🔍 Troubleshooting

**Antigravity can't find skills:**
Skills must physically exist at `~/.gemini/antigravity/skills/`. Do not move them.

**Claude Code can't find commands/skills:**
Run `~/dot/setup.sh` to recreate symlinks.

**OpenCode can't find skills:**
Verify `~/.config/opencode/skills/` symlink exists and points to antigravity.

---

**Source**: `marcdhansen/dot` — `setup.sh` is authoritative for symlink creation.
