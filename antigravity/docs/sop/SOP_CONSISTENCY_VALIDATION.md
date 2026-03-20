# SOP Consistency Validation

**Purpose**: Automated validation of cross-agent Standard Operating Procedure (SOP) compliance.

## Overview

The SOP Consistency Validator ensures that all agent directories (`.agent`, `.gemini`, `.config`, `.antigravity`) maintain consistency with cross-agent protocols. It runs automatically during the Finalization process.

## Usage

### Manual Execution

```bash
# Validate current project
python ~/.agent/scripts/validate_sop_consistency.py

# Validate specific project
python ~/.agent/scripts/validate_sop_consistency.py --project-dir /path/to/project

# Verbose output
python ~/.agent/scripts/validate_sop_consistency.py --verbose
```

The validator runs automatically during Orchestrator Finalization checks:

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --finalize
```

## Validation Checks

### 1. Global Directory Structure

- ✅ `~/.agent/` exists (Universal standards)
- ✅ `~/.gemini/` exists (Provider-specific configs)
- ✅ `~/.antigravity/` exists (Global workflows/skills)

### 2. Project Structure

- ✅ `.agent/rules/` exists (Project-specific planning)
- ✅ `.agent/skills/` exists (Project-specific extensions)
- ✅ `.agent/docs/` exists (Project documentation)
- ✅ `.agent/scripts/` exists (Project automation)
- ✅ `.agent/session_locks/` exists (Multi-agent coordination)

### 3. Symlink Integrity

- ✅ `docs/sop/global-configs` → `~/.agent/docs/`
- ✅ `docs/sop/skills` → `.agent/skills/`
- ✅ `BOOTSTRAP.md` → `~/.gemini/AGENT_ONBOARDING.md`
- ❌ Detects and blocks circular symlinks (e.g., `~/.gemini/.gemini`)

#### 3.1 Skills & Commands Symlink Ecosystem (Critical Validation)

**🚨 BLOCKING**: Finalization blocked if any critical symlinks are broken

**Skills Access Points**:

- ✅ `.agent/skills/` → `~/.gemini/antigravity/skills/`
- ✅ `~/.config/opencode/skills/` → `~/.gemini/antigravity/skills/`

**Commands & Workflows Access Points**:

- ✅ `~/.agent/commands/` → `~/.gemini/antigravity/global_workflows/`
- ✅ `~/.config/opencode/commands/` → `~/.gemini/antigravity/global_workflows/`
- ✅ `.agent/workflows/next.md` → `~/.gemini/antigravity/global_workflows/next.md`
- ✅ `.agent/workflows/finalization.md` → `~/.gemini/antigravity/global_workflows/wtu.md`

**Validation Logic**:

```bash
# Critical skills symlinks (BLOCKING)
if [[ ! -L ".agent/skills" ]] || [[ "$(readlink .agent/skills)" != "$(echo ~/.gemini/antigravity/skills/)" ]]; then
    echo "🚨 CRITICAL: .agent/skills symlink broken - Finalization BLOCKED"
    exit 2
fi

# Critical commands symlinks (BLOCKING)
if [[ ! -L "~/.agent/commands" ]] || [[ "$(readlink ~/.agent/commands)" != "$(echo ~/.gemini/antigravity/global_workflows/)" ]]; then
    echo "🚨 CRITICAL: ~/.agent/commands symlink broken - Finalization BLOCKED"
    exit 2
fi
```

### 4. File Consistency

- ✅ Universal entry point exists: `~/.agent/AGENTS.md`
- ✅ Single source of truth for `GLOBAL_INDEX.md` in `~/.agent/docs/`
- ✅ No duplicate critical files

### 5. File Placement Compliance

Ensures files are in correct directories per SOP:

**Global Standards** (`~/.agent/`):

- `AGENTS.md` - Universal entry point
- `GLOBAL_INDEX.md` - Global navigation (in `docs/`)
- Universal SOPs (in `docs/sop/`)

**Provider-Specific** (`~/.gemini/`):

- `INITIALIZATION.md` - Gemini-specific onboarding
- `GEMINI.md` - Gemini agent configuration
- Provider-specific authentication and settings

**Project-Specific** (`<Project>/.agent/`):

- `rules/ROADMAP.md` - Project roadmap
- `rules/ImplementationPlan.md` - Technical plan
- Project-specific skills and extensions

### 6. Git Status Monitoring

- ✅ Checks for uncommitted changes in global directories
- ⚠️ Warns about uncommitted changes that should be committed

### 7. Markdown Quality

- ✅ Runs `markdownlint` on key documentation files
- ⚠️ Reports formatting issues that may affect readability

## Exit Codes

- **0**: All checks passed ✅
- **1**: Warnings found (non-blocking) ⚠️
- **2**: Errors found (blocking) 🚨

## Common Issues and Solutions

### Circular Symlinks

**Error**: `Circular symlink detected: ~/.gemini/.gemini`
**Solution**: Remove circular reference

```bash
rm ~/.gemini/.gemini
```

### Missing Expected Symlinks

**Warning**: `Missing expected symlink: docs/sop/global-configs`
**Solution**: Create missing symlinks to global standards

### Critical Skills/Commands Symlinks Broken

**Error**: `🚨 CRITICAL: .agent/skills symlink broken - Finalization BLOCKED`
**Solution**: Recreate critical symlinks to universal source

```bash
# Fix broken skills symlinks
rm .agent/skills ~/.config/opencode/skills 2>/dev/null
ln -sf ~/.gemini/antigravity/skills/ .agent/skills/
ln -sf ~/.gemini/antigravity/skills/ ~/.config/opencode/skills/

# Fix broken commands symlinks  
rm ~/.agent/commands ~/.config/opencode/commands 2>/dev/null
ln -sf ~/.gemini/antigravity/global_workflows/ ~/.agent/commands/
ln -sf ~/.gemini/antigravity/global_workflows/ ~/.config/opencode/commands/

# Fix broken project workflow symlinks
rm .agent/workflows/next.md .agent/workflows/finalization.md 2>/dev/null
ln -sf ~/.gemini/antigravity/global_workflows/next.md .agent/workflows/next.md
ln -sf ~/.gemini/antigravity/global_workflows/wtu.md .agent/workflows/finalization.md
```

### Multiple GLOBAL_INDEX.md Files

**Warning**: `Multiple GLOBAL_INDEX.md files found`
**Solution**: Choose single source of truth, remove duplicates

### Uncommitted Changes in Global Directories

**Warning**: `Uncommitted changes in ~/.gemini:`
**Solution**: Commit changes to maintain consistency across agents

```bash
cd ~/.gemini && git add -A && git commit -m "Update global standards"
```

## Integration with Orchestrator

The SOP validator is integrated into the Orchestrator Finalization process:

1. **Critical Errors**: Block Finalization completion (exit code 2)
2. **Warnings**: Allow Finalization with warnings (exit code 1)
3. **Success**: Continue with normal Finalization flow

This ensures that:

- All agents maintain consistent directory structure
- Single source of truth principle is preserved
- Cross-agent compatibility is maintained
- Documentation integrity is verified

## Troubleshooting

### Permission Denied Errors

Some validation checks require access to global directories. Ensure the agent has appropriate permissions.

### Missing Tools

- `markdownlint`: Optional - skipped if not available
- `git`: Required for git status checks

### Timeout Issues

Network-dependent operations (like git status) have timeouts to prevent hanging.

## Maintenance

The validator should be updated when:

- New global directories are added
- File placement rules change
- New validation requirements are identified
- Directory structure evolves
- **New skills or commands are added to the ecosystem**
- **Symlink access points are modified**
- **Cross-tool integration patterns change**

---

**Location**: `~/.agent/scripts/validate_sop_consistency.py`  
**Integrated**: Orchestrator Finalization process  
**Purpose**: Cross-agent SOP compliance validation
