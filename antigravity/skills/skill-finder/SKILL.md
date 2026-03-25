---
name: skill-finder
description: Find existing skills before creating new ones. Searches marketplaces, GitHub, and local skills.
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep, web_search
---

# Skill: skill-finder

**Purpose**: Find existing skills before creating new ones. Prevents duplicate work and leverages the community.

## Usage

```bash
/skill-finder [task description]
```

## What It Does

1. Searches Anthropic's official skills repo
2. Searches Alireza Rezvan's comprehensive collection (183+ skills)
3. Searches LobeHub marketplace (100,000+ skills)
4. Checks MCP Market for compatible skills
5. Checks locally installed skills
6. Provides a recommendation report

## Skill Marketplaces

| Marketplace | URL | Skills | Platform |
|-------------|-----|--------|----------|
| Anthropic Official | github.com/anthropics/skills | ~50 | Claude Code, Claude.ai |
| Alireza Rezvan | github.com/alirezarezvani/claude-skills | 183+ | 11 platforms |
| LobeHub | lobehub.com/skills | 100,000+ | Various |
| MCP Market | mcpmarket.com/tools/skills | MCP skills | MCP-compatible |
| skillsmp.com | skillsmp.com | Community | Claude |

## Search Strategy

### 1. Web Search

Search for: `[task] skill claude` or `[task] agent skill opencode`

### 2. GitHub Search

```bash
# Search GitHub for skill repositories
gh search repos "claude skill [task]" --limit 10
```

### 3. Local Check

```bash
# Check installed skills
ls ~/.config/opencode/skills/
ls ~/.claude/skills/
```

### 4. Marketplace Search

Use web search to search:
- https://github.com/anthropics/skills
- https://github.com/alirezarezvani/claude-skills
- https://lobehub.com/skills

## Output Format

```markdown
# Skill Search Report: [task]

## Search Results

| Source | Found | Skill Name | URL |
|--------|-------|------------|-----|
| Anthropic | ❌ | - | - |
| Alireza Rezvan | ✅ | some-skill | github.com/... |
| LobeHub | ❌ | - | - |
| MCP Market | ❌ | - | - |
| Local | ❌ | - | - |

## Recommendation

✅ **Use existing**: some-skill
❌ **Create new**: No suitable skill found

## Action Items

- [ ] Install some-skill from alirezarezvani/claude-skills
- [ ] Test in your environment
```

## Installation from GitHub

### Anthropic Skills

```bash
# Add as Claude Code plugin marketplace
/plugin marketplace add anthropics/skills

# Install specific skill
/plugin install document-skills@anthropic-agent-skills
```

### Alireza Rezvan Skills

```bash
# Add marketplace
/plugin marketplace add alirezarezvani/claude-skills

# Install skill bundle
/plugin install @claude-code-skills
```

### Manual Install

```bash
# Clone repository
git clone https://github.com/[author]/[skill-repo].git

# Copy skill to local skills directory
cp -r [skill-repo]/skills/[skill-name] ~/.config/opencode/skills/
```

## Decision Matrix

| Found | Action |
|-------|--------|
| Perfect match | Use as-is |
| Partial match | Adapt existing |
| No match | Create new |

## Skill Evaluation Checklist

**ALWAYS evaluate a skill before adopting it.**

### Security

- [ ] No hardcoded secrets/API keys
- [ ] Handles credentials securely (env vars, not files)
- [ ] No suspicious network calls
- [ ] Sandboxed appropriately
- [ ] MCP tools have proper access controls

### Quality

- [ ] Active maintenance (commits in last 6 months)
- [ ] Has tests
- [ ] No obvious bugs or anti-patterns
- [ ] Clear documentation
- [ ] No excessive dependencies

### Compatibility

- [ ] Works with our platform (OpenCode)
- [ ] Compatible Python version (3.9+)
- [ ] No conflicting dependencies
- [ ] Works non-interactively (CI-safe)

### Trust

- [ ] Known author/reputation
- [ ] Open source license (MIT, Apache, etc.)
- [ ] Community reviewed
- [ ] No malicious patterns in code

### Evaluation Report Template

```markdown
# Skill Evaluation: [skill-name]

## Candidate Info
- **Source**: github.com/author/repo
- **Author**: [author]
- **License**: MIT
- **Last Update**: 2026-03-01

## Checklist

### Security
- [✅/❓/❌] No hardcoded secrets
- [✅/❓/❌] Secure credential handling
- [✅/❓/❌] No suspicious network calls
- [✅/❓/❌] Proper sandboxing

### Quality
- [✅/❓/❌] Active maintenance
- [✅/❓/❌] Has tests
- [✅/❓/❌] Clear documentation
- [✅/❓/❌] Minimal dependencies

### Compatibility
- [✅/❓/❌] Works with OpenCode
- [✅/❓/❌] Python 3.9+ compatible
- [✅/❓/❌] CI-safe (non-interactive)

### Trust
- [✅/❓/❌] Known author
- [✅/❓/❌] Open source license
- [✅/❓/❌] Community reviewed

## Verdict

| Category | Score |
|----------|-------|
| Security | X/Y |
| Quality | X/Y |
| Compatibility | X/Y |
| Trust | X/Y |
| **TOTAL** | X/Y |

### Decision

✅ **APPROVE**: All checks pass, safe to use
⚠️ **ADAPT**: Minor issues, adapt before use
❌ **REJECT**: Security/quality concerns

## Notes

[Add specific observations]
```

## Tips

1. **Broad search first**: Try general terms like "testing", "research", "planning"
2. **Check forks**: A skill might exist but not be in the main repo
3. **Platform matters**: Some skills only work on specific platforms (Claude Code vs Claude.ai)
4. **Cross-platform**: Alireza Rezvan's skills work on 11 platforms including OpenCode

## Related Skills

- **skill-making**: Create new skills after confirming none exist
- **research**: Research topics and technologies
