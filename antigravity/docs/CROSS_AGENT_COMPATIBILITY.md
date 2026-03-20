# Cross-Agent Compatibility Strategy

> **Scope**: Universal SOP enforcement across all agent providers  
> **Status**: Phase 2 Implementation Complete  
> **Last Updated**: 2026-02-08

---

## 🎯 Executive Summary

Universal SOP compliance is achieved through **external enforcement gates** and **symlink-based single source of truth**. This strategy ensures all agents (Gemini, OpenCode, Claude Code, Cursor) follow the same protocols regardless of their provider-specific configurations.

---

## 🏗️ Architecture Overview

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Universal Session Gate** | External enforcement that agents cannot bypass | `~/.agent/bin/agent-session-gate` |
| **Session Audit Logger** | Centralized logging and compliance tracking | `~/.agent/bin/session-audit-log` |
| **Universal Protocols** | Single source of truth for all agents | `~/.agent/AGENTS.md` |
| **SOP Compliance Checklist** | Complete compliance requirements | `~/.agent/docs/SOP_COMPLIANCE_CHECKLIST.md` |
| **Orchestrator Skill** | Validation and enforcement logic | `~/.gemini/antigravity/skills/Orchestrator/` |

---

## 🔗 Provider Integration Matrix

| Provider | Session Start Hook | Configuration Method | Status | Enforcement |
|----------|-------------------|---------------------|--------|-------------|
| **OpenCode** | `opencode.json` instructions | Global config + symlinks | ✅ **ACTIVE** | Pre-commit hooks |
| **Gemini/Antigravity** | `GEMINI.md` auto-execute | Universal session gate | ✅ **ACTIVE** | External gate |
| **Claude Code** | `CLAUDE.md` + `claude.json` | Symlink + JSON config | ✅ **ACTIVE** | Pre-commit hooks |
| **Cursor** | `.cursorrules` | Project-level rules | 🔄 **PLANNED** | Pre-commit hooks |

---

## 📁 Symlink Strategy (Single Source of Truth)

### Global Configuration Links

```bash
# OpenCode Configuration (PRIMARY)
~/.config/opencode/AGENTS.md → ~/.agent/AGENTS.md  ✅ ACTIVE
~/.config/opencode/skills    → ~/.gemini/antigravity/skills ✅ ACTIVE

# Claude Code Configuration
~/.claude/CLAUDE.md → ~/.agent/AGENTS.md  ✅ ACTIVE
~/.claude/claude.json → SOP instructions  ✅ ACTIVE

# Universal Bootstrap (All Providers)
~/.agent/BOOTSTRAP.md → Cross-provider reference  ✅ ACTIVE
```

### Benefits

- ✅ **Single Source of Truth**: Changes propagate instantly to all providers
- ✅ **No Sync Issues**: No duplicate files to maintain
- ✅ **Universal Updates**: One update affects all agents
- ✅ **Provider Agnostic**: Works with any agent system

---

## 🚪 Universal Session Gate

### Purpose
External enforcement that runs **before** any agent gets control. Agents cannot bypass this gate.

### Implementation
```bash
# Universal entry point for all agents
~/.agent/bin/agent-session-gate

# Provider-specific usage
export AGENT_PROVIDER=opencode && ~/.agent/bin/agent-session-gate
export AGENT_PROVIDER=gemini && ~/.agent/bin/agent-session-gate
export AGENT_PROVIDER=claude && ~/.agent/bin/agent-session-gate
```

### Gate Functions
1. **SOP Validation**: Runs Orchestrator compliance checks
2. **Session Logging**: Creates audit trail entry
3. **Environment Setup**: Configures enforcement variables
4. **Bypass Prevention**: Sets up pre-commit hook validation

---

## 📊 Audit Trail System

### Session Logging Format
```
TIMESTAMP | EVENT | PROVIDER | WORKSPACE | SESSION_ID | DETAILS
```

### Key Events Tracked
- `SESSION_START`: Agent session initialization
- `SESSION_INITIALIZED`: Successful gate completion
- `VALIDATION_FAILED`: SOP compliance failures
- `SESSION_END`: Session completion (success/failure)
- `COMMIT_BLOCKED`: Pre-commit hook enforcement
- `HOOK_TAMPERED`: Hook integrity violations

### Audit Tools
- **session-audit-log**: Python-based logging and analysis
- **sop-audit-report**: Bash-based reporting dashboard
- **compliance_log.json**: Structured data for analysis

---

## 🛡️ Enforcement Mechanisms

### 1. Pre-commit Hook Integration
```yaml
# .pre-commit-config.yaml (all repositories)
- id: sop-compliance-check
  name: 🔍 SOP Compliance Check
  entry: python3 /path/to/check_protocol_compliance.py
  args: [--finalize, --turbo]
  always_run: true
  stages: [pre-commit]
```

### 2. Hook Tampering Detection
```python
# Orchestrator enhancement
def check_hook_integrity():
    """Detect if pre-commit hooks were modified or removed."""
    # Validates hook file existence and content patterns
    # Blocks commits if hooks are tampered with
```

### 3. Environment Variable Enforcement
```bash
# Set by session gate, checked by hooks
export AGENT_SESSION_VALIDATED=true
export AGENT_SESSION_ID=<unique-id>
export AGENT_PROVIDER=<provider>
```

---

## 🔄 Provider-Specific Configurations

### OpenCode (Primary Focus)
```json
// ~/.config/opencode/opencode.json
{
  "instructions": [
    "~/.agent/AGENTS.md",
    "~/.agent/docs/SOP_COMPLIANCE_CHECKLIST.md",
    "~/.gemini/antigravity/skills/Orchestrator/SKILL.md"
  ]
}
```

### Claude Code
```json
// ~/.claude/claude.json
{
  "instructions": [
    "~/.claude/CLAUDE.md",
    "~/.agent/docs/SOP_COMPLIANCE_CHECKLIST.md",
    "~/.gemini/antigravity/skills/Orchestrator/SKILL.md"
  ]
}
```

### Gemini/Antigravity
```markdown
// ~/.gemini/GEMINI.md
## Session Initialization
```bash
export AGENT_PROVIDER=gemini
~/.agent/bin/agent-session-gate
```
```

### Cursor (Planned)
```markdown
// .cursorrules (project-level)
# Cursor Agent Configuration

## Session Start
Before any work, run:
```bash
export AGENT_PROVIDER=cursor
~/.agent/bin/agent-session-gate
```
```

---

## 📈 Success Metrics

### Quantitative Metrics
- **Compliance Rate**: >95% sessions passing all checks
- **Bypass Prevention**: 100% commits blocked without validation
- **Cross-Provider Coverage**: 100% providers have enforcement
- **Audit Trail Coverage**: 100% sessions logged

### Qualitative Metrics
- **Reduced SOP Violations**: Fewer violations in retrospectives
- **Improved Coordination**: Better multi-agent coordination
- **Universal Consistency**: Same behavior across providers
- **Enhanced Accountability**: Clear audit trail for all activity

---

## 🚨 Bypass Prevention Strategy

### External Enforcement
- **Session Gate**: Runs outside agent control
- **Pre-commit Hooks**: Block non-compliant git operations
- **Hook Integrity**: Detect and prevent tampering
- **Audit Trail**: Log all bypass attempts

### Red Team Scenarios
| Bypass Attempt | Mitigation |
|---------------|------------|
| Agent skips session gate | Pre-commit hooks block without validation |
| Agent modifies hooks | Hook tampering detection blocks commits |
| Agent uses different git identity | Audit trail logs all activity |
| Agent commits directly to main | Branch protection + hooks block |

---

## 🔧 Implementation Checklist

### Phase 2 Complete ✅
- [x] Universal session gate script
- [x] Session audit logging system
- [x] Claude Code configuration
- [x] Updated Gemini configuration
- [x] SOP audit report tool
- [x] Cross-agent compatibility documentation

### Phase 3 (Future)
- [ ] Cursor integration
- [ ] Advanced bypass detection
- [ ] Real-time monitoring dashboard
- [ ] Automated compliance scoring

---

## 🛠️ Troubleshooting

### Common Issues

**Session gate fails to start**
```bash
# Check permissions
ls -la ~/.agent/bin/agent-session-gate

# Check Orchestrator
python3 ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --init --turbo
```

**Pre-commit hooks not working**
```bash
# Reinstall hooks
pre-commit install --all-types

# Check hook integrity
python3 ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize
```

**Audit log not created**
```bash
# Check directory permissions
ls -la ~/.agent/logs/

# Test audit logger
~/.agent/bin/session-audit-log --log --event TEST --provider test
```

---

## 📚 Additional Resources

- [Universal Agent Protocols](~/.agent/AGENTS.md)
- [SOP Compliance Checklist](~/.agent/docs/SOP_COMPLIANCE_CHECKLIST.md)
- [Orchestrator Skill Documentation](~/.gemini/antigravity/skills/Orchestrator/SKILL.md)
- [Session Audit Tool](~/.agent/bin/session-audit-log --help)
- [SOP Audit Report](~/.agent/bin/sop-audit-report --help)

---

*This strategy ensures universal SOP compliance across all agent providers through external enforcement and single source of truth architecture.*