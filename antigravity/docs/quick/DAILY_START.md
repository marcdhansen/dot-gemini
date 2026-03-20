# ⚡ Daily Start (< 20 lines)

**Returning agent? Start productive work in seconds.**

---

## 🚀 **3 Commands to Work**

```bash
# 1. Register your session (auto-detects requirements)
./scripts/agent-start.sh --task-id <task-id> --task-desc "brief description"

# 2. See available work
bd ready

# 3. Work on your task...
# (use your normal workflow)

# 4. End session (cleanup everything)
./scripts/agent-end.sh
```

---

## ⚡ **Session Examples**

```bash
# Example 1: Task from Beads
./scripts/agent-start.sh --task-id lightrag-vtt --task-desc "Standardize ~/.agent/ structure"
bd ready

# Example 2: Custom work
./scripts/agent-start.sh --task-id custom-fix --task-desc "Quick bug fix"
# Work...
./scripts/agent-end.sh
```

---

## 🔧 **Enhanced Services (Optional)**

Need Langfuse tracing or Automem memory?

```bash
# Enhanced session (auto-starts services)
./scripts/enhanced-agent-init.sh --task-id <task-id> --task-desc "description"

# Or manually enable after session start
./scripts/start-services.sh
```

---

## ✅ **Success Indicators**

✅ Session locked and heartbeat started  
✅ Task exclusivity verified  
✅ Resources allocated (ports, worktree)  
✅ Git hooks active  
✅ Ready for collaborative work  

---

**Need help?** → [Just-in-Time Help](../AGENTS.md#-just-in-time-help)  
**First time here?** → [First Time Setup](FIRST_TIME_SETUP.md)
