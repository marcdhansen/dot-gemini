# 🌟 Gemini Agent Configuration

**Scope**: **PROVIDER-SPECIFIC** — This file is ONLY for Gemini/Google-specific configuration.
> [!IMPORTANT]
> **NO UNIVERSAL PROTOCOLS**: Do not add SOP, Initialization, or Finalization procedures here. All universal protocols must reside in `~/.agent/AGENTS.md`.

**Purpose**: Gemini-specific configuration and capabilities.

## 🚀 **Universal Standards**

For universal agent protocols, protocols, and documentation:
→ **Read** [~/.agent/AGENTS.md](~/.agent/AGENTS.md)

## 🔧 **Gemini-Specific Configuration**

- Google Accounts: [google_accounts.json](google_accounts.json)
- Agent State: [state.json](state.json)
- Provider Settings: (various config files)

## 📚 **Complete Navigation**

→ **Master Index**: [~/.agent/docs/GLOBAL_INDEX.md](/Users/marchansen/.agent/docs/GLOBAL_INDEX.md)

---

## 🧬 Gemini Specific Memories

- **System File Locations (Gemini)**:
  - Global Rules: `~/.gemini/GEMINI.md`
  - Global Workflows: `~/.gemini/antigravity/global_workflows/global-workflow.md`
  - Project Brain/Planning: `~/.gemini/antigravity/brain/PROJECT_ID/`

---

*Last Updated: 2026-02-02*
*Gemini Specific Configuration*

---

## 🚀 Session Initialization (Auto-Execute)

> [!CAUTION]
> **FIRST ACTION of every session**: Before responding to ANY user request, execute these commands:

// turbo

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --init --turbo
python ~/.gemini/antigravity/skills/initialization-briefing/initialization_briefing.py --turbo
```

**This is NON-NEGOTIABLE** - run these before any other work.
