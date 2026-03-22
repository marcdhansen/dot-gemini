# 🏗️ Cross-IDE & Cross-Agent Compatibility Design

This document outlines the architectural decisions that ensure the Universal Agent Protocol
remains consistent across all IDEs and AI agents.

---

## 🎯 Core Design Principle: Provider Doc Separation

Each agent reads **two** files at session start:
1. `~/.agent/AGENTS.md` — universal rules (applies to all agents)
2. Their provider-specific doc — only what differs per agent

| Agent | Universal rules | Provider-specific |
|:------|:---------------|:-----------------|
| Gemini / Antigravity | `~/.agent/AGENTS.md` | `~/.gemini/GEMINI.md` |
| Claude Code / Claude.ai | `~/.agent/AGENTS.md` (via `~/.claude/CLAUDE.md` symlink) | `~/.claude/README.md` |
| OpenCode | `~/.agent/AGENTS.md` (via `~/.config/opencode/AGENTS.md` symlink) | `~/.config/opencode/opencode.json` |

**Rule:** If a piece of information applies to all agents, it belongs in `~/.agent/AGENTS.md` — NOT
in provider docs. Provider docs contain ONLY what is specific to that agent/IDE.
This avoids duplication and ensures all agents see the same universal rules.

---

## 🏠 Home Directory Structure

```
~/.agent/          ← Universal hub (dot-agent repo)
  AGENTS.md        ← Universal instructions — all agents read this
  BOOTSTRAP.md     ← Paste into web sessions without MCP access
  bin/             ← Scripts (agent-session-gate, etc.)
  docs/            ← Documentation
  skills/          → ~/.gemini/antigravity/skills/  (symlink — see below)
  commands/        → ~/.gemini/antigravity/global_workflows/  (symlink)

~/.gemini/         ← Gemini + Antigravity (dot-gemini repo)
  GEMINI.md        ← Gemini/Antigravity-specific config only
  antigravity/
    skills/        ← CANONICAL SKILL SOURCE (actual directory)
    global_workflows/ ← CANONICAL WORKFLOW SOURCE (actual directory)

~/.claude/         ← Claude config (managed by setup.sh)
  CLAUDE.md        → ~/.agent/AGENTS.md  (symlink)
  README.md        ← Claude-specific session init (MCP tools, etc.)
  skills/          → ~/.gemini/antigravity/skills/  (symlink)
  commands/        → ~/.gemini/antigravity/global_workflows/  (symlink)

~/.config/opencode/ ← OpenCode (dot-opencode repo)
  AGENTS.md        → ~/.agent/AGENTS.md  (symlink)
  skills/          → ~/.gemini/antigravity/skills/  (symlink)
  commands/        → ~/.gemini/antigravity/global_workflows/  (symlink)
```

---

## ⚠️ The Antigravity Symlink Constraint

Skills and workflows physically live in `~/.gemini/antigravity/` because
**Antigravity IDE cannot follow symlinks**. All other agents work around this
by symlinking TO antigravity rather than FROM it.

This is a **workaround, not a design choice**. The intended canonical home
is `~/.agent/skills/`. When Antigravity gains symlink support, the direction
will reverse. Until then, all skill development happens in
`~/.gemini/antigravity/skills/`.

See `~/.agent/docs/architecture/SYMLINKS.md` for the complete symlink map.

---

## 🛠️ Implementation Standards

### Shell-Obsessed Tooling
All critical operations must be executable via a standard terminal (zsh/bash).
If a tool requires a GUI or IDE-specific plugin, it is not protocol-compliant.

### Markdown as Common Tongue
Standard GitHub-flavored Markdown is the only approved format for planning
and documentation — readable by all LLM providers.

### Beads for Task Tracking
`bd` (Beads) with a git-backed database eliminates centralized project management:
- Any agent runs `bd ready` to find work
- Any agent runs `bd sync` to synchronize
- Source: `~/GitHub/beads` — install: `cd ~/GitHub/beads && go install ./cmd/bd`

### The Orchestrator
Implemented as a standalone Python suite at
`~/.gemini/antigravity/skills/Orchestrator/`. Invoked via standard Python,
so any agent that can run shell commands can validate SOP compliance.

---

## 🚀 Onboarding a New Agent or IDE

1. Ensure `~/.agent/AGENTS.md` is accessible (symlink or direct read)
2. Create a provider-specific doc with ONLY agent-specific initialization
3. Add symlinks to skills and commands pointing at `~/.gemini/antigravity/`
4. Run `~/dot/setup.sh` to create standard symlinks

See `docs/ONBOARDING.md` for detailed steps.

---

## 🧬 Self-Evolution

The `reflect` skill captures session learnings. Universal insights update
`~/.agent/AGENTS.md`. Provider-specific insights update the relevant
provider doc (`~/.gemini/GEMINI.md`, `~/.claude/README.md`, etc.).

---

## 🔗 Navigation

- **[Global Index](GLOBAL_INDEX.md)** — entry point for all documentation
- **[SYMLINKS.md](architecture/SYMLINKS.md)** — complete symlink reference
- **[ARCHITECTURE.md](architecture/ARCHITECTURE.md)** — four-repo design and rationale
- **[Beads Guide](BEADS_GUIDE.md)** — task tracking across agents
