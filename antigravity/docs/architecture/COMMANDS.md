# ⚡ Commands & Workflows Ecosystem Guide

**Purpose**: Complete documentation of slash commands and workflow system.
**Target**: Advanced users needing comprehensive command understanding.
**Ecosystem Tier**: Tier 2 - Detailed Guide (separate ecosystem document)

---

## 🌐 **Commands Symlink Ecosystem**

### **Source of Truth**

```bash
~/.gemini/antigravity/global_workflows/  ← Universal Global Workflows Repository
```

### **Access Points (Symlinks)**

```bash
Global Agent Access:  ~/.agent/commands/ → ~/.gemini/antigravity/global_workflows/
OpenCode Global:     ~/.config/opencode/commands/ → ~/.gemini/antigravity/global_workflows/
Workspace-Specific:  .agent/workflows/ → Project-local workflows (managed locally)
```

---

## 📁 **Command System Architecture**

### **Global Workflows (Universal)**

```bash
~/.gemini/antigravity/global_workflows/
├── wtu.md              # Finalization/Retrospective workflow (formerly rtb)
├── next.md             # Task discovery workflow
├── reflect.md          # Session reflection workflow
└── [other-workflows].md # Additional global workflows
```

---

## ⚡ **Available Commands (Complete Catalog)**

### **🛬 Core System Commands**

#### **`/wtu` - Wrap This Up (Finalization & Retrospective)**

**Purpose**: Complete Finalization workflow with validation
**Usage**: End-of-session validation and cleanup (MANDATORY)

**Key Features**:

- Validates git repository status
- Runs project-specific quality gates
- Ensures proper session completion
- Blocks completion if validation fails

#### **`/next` - Task Discovery**

**Purpose**: Discover available tasks and current priorities
**Usage**: Task assignment and workflow navigation

**Key Features**:

- Integrates with `bd ready` command
- Prioritizes tasks based on dependencies
- Provides detailed task context

#### **`/reflect` - Session Reflection**

**Purpose**: Capture session learnings and continuous improvement
**Usage**: End-of-session analysis and learning capture

**Key Features**:

- Analyzes conversation for learning opportunities
- Captures user preferences and corrections
- Updates skill documentation automatically

---

## 🔗 **Tool-Specific Integration**

### **Antigravity Integration**

```bash
# Commands through Antigravity agent system
ls .agent/workflows/  # → workspace-specific workflows

# Usage in Antigravity context
/wtu    # Direct availability
/next   # Direct availability
/reflect # Direct availability
```

---

**Last Updated**: 2026-02-06
**Part of**: Documentation System (Tier 2 - Commands Ecosystem)
**Scope**: Universal Commands Documentation
