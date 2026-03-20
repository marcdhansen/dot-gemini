# 🔗 Complete Symlink Ecosystem Reference

**Purpose**: Comprehensive technical reference for symlink architecture.
**Target**: System administrators and advanced troubleshooting.
**Ecosystem Tier**: Tier 3 - Complete Technical Reference

---

## 🏗️ **System Architecture Overview**

### **Core Principle: Symlink Exception**

**Standard Rule**: `.agent/` directory is single source of truth.
**Exception**: Skills and commands use `~/.gemini/antigravity/` as universal source.

### **Why This Architecture?**

1. **Prevents Breakage**: `~/.gemini` with symlinks causes system failures.
2. **Universal Resource Sharing**: Multiple tools access same capabilities.
3. **Cross-Project Compatibility**: Consistent access across all workspaces.

---

## 🌐 **Complete Symlink Map**

### **Skills Ecosystem**

```bash
~/.gemini/antigravity/skills/                    ← UNIVERSAL SOURCE OF TRUTH
├── reflect/
├── finalization/
├── show-next-task/
├── Orchestrator/
└── [other-skills]

↓ SYMLINK ACCESS POINTS ↓
.agent/skills/ → ~/.gemini/antigravity/skills/
```

### **Commands & Workflows Ecosystem**

```bash
~/.gemini/antigravity/global_workflows/          ← UNIVERSAL SOURCE OF TRUTH
├── wtu.md (formerly rtb.md)
├── next.md
└── reflect.md

↓ SYMLINK ACCESS POINTS ↓
~/.agent/commands/ → ~/.gemini/antigravity/global_workflows/
```

---

**Last Updated**: 2026-02-06
**Part of**: Documentation System (Tier 3 - Complete Technical Reference)
**Scope**: Universal Symlink Architecture
