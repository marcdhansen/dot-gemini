# Renaming Project to LightRAG_gemini

This plan renames the project from `LightRAG_claude` to `LightRAG_gemini` to better reflect the use of Gemini as the primary agent assistant.

## User Review Required

> [!IMPORTANT]
> I am renaming the Git remote URL to `https://github.com/marcdhansen/LightRAG_gemini.git`. Please ensure this repository exists on GitHub if you intend to push to it.
>
> [!NOTE]
> I am also renaming references to "Claude Code" and ".claude/" in `.gitignore` to ".gemini/" and "Gemini Code".

## Proposed Changes

### Git Configuration

#### [MODIFY] [.git/config](file:///Users/marchansen/claude_test/LightRAG/.git/config)
- Update remote "origin" URL from `https://github.com/marcdhansen/LightRAG_claude.git` to `https://github.com/marcdhansen/LightRAG_gemini.git`.

### Documentation & Infrastructure

#### [MODIFY] [.gitignore](file:///Users/marchansen/claude_test/LightRAG/.gitignore)
- Replace `.claude/` with `.gemini/`
- Replace `CLAUDE.md` with `GEMINI.md`
- Update comments from "Claude Code" to "Gemini Code"

#### [MODIFY] [AGENT_INSTRUCTIONS.md](file:///Users/marchansen/claude_test/.agent/rules/AGENT_INSTRUCTIONS.md)
- Update paths and references if any (already checked, but will double-check during execution).

### Beads Configuration

#### [MODIFY] Beads Config
- Run `bd config set compact_model gemini-1.5-pro` (or similar) to switch away from Claude models for compaction.

## Verification Plan

### Automated Tests
- Run `git remote -v` to verify URL change.
- Run `grep -r "claude" .` (excluding legitimate LLM files) to ensure no forgotten references.

### Manual Verification
- Verify that `.gitignore` correctly reflects the new agent file structure.
- Verify `bd config list` shows updated model.
