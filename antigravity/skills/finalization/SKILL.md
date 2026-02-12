---
name: finalization
description: Performs Finalization checks and completes session closure. Validates git status, runs quality gates, updates issue status, and ensures proper session closure.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# Finalization Execution Skill

The `finalization` skill performs the actual finalization protocol when called by an agent.

## Usage

```bash
/finalization
```

## Purpose

Performs comprehensive Finalization checks to ensure:

- All work is committed and pushed to remote
- Quality gates have been passed
- Issue status is properly updated
- Session closure is complete
- Next session has proper context (including mandatory Beads Issue ID)

## Implementation

The skill executes:

```bash
~/.gemini/antigravity/skills/finalization/scripts/finalization.sh
```

## Workflow Steps

1. **Pre-Finalization Validation**
   - Check current git status
   - Identify uncommitted changes
   - Validate branch state

2. **Quality Gates** (if code changed)
   - Run tests (if available)
   - Run linting/typechecking (if configured)
   - Build validation (if applicable)

3. **Markdown Duplication Check** (Mandatory)
   - Run mandatory markdown verification
   - BLOCKER if duplicate files exist

4. **SOP Evaluation** (Mandatory)
   - Evaluate SOP effectiveness and Initialization compliance
   - BLOCKER if SOP evaluation fails

5. **Issue Management**
   - Check for open beads issues
   - Update issue status via `bd` commands
   - Close completed tasks
   - **NEW: Remind about closure notes requirements**

6. **Reflection Capture** (Mandatory)
   - Run reflection skill/script automatically
   - Capture session learnings systematically
   - Fallback to basic reflection if skill unavailable

7. **Git Operations**
   - Pull latest changes with rebase
   - Sync beads database
   - Push all changes to remote
   - Verify clean git status

8. **Session Closure**
   - Clear temporary files
   - Pruning stale branches
   - Update session locks

9. **Global Memory Sync**
   - Commit learnings to `~/.gemini`
   - Push global memory changes

## Exit Conditions

## Finalization Error Handling

If Finalization fails:

1. Check for merge conflicts - resolve and retry
2. Verify network connectivity for git operations
3. Check beads daemon status (`bd daemon status`)
4. Review error logs in automation scripts
5. Manual intervention may be required for certain edge cases

## 🚨 Critical Fix Applied: Auto-Commit Missing Files

**Issue**: RTB process could miss uncommitted files (like rag storage files)  
**Learning**: Finalization must auto-commit ALL remaining changes, not just initial git status  
**Solution Implemented**: Enhanced auto-commit section in finalization.sh

```bash
# Auto-commit ALL remaining uncommitted changes to prevent Finalization failures
if [ ! -z "$GIT_STATUS" ]; then
    echo "🔧 Auto-committing remaining uncommitted changes..."
    git add -A
    git commit -m "rtb-auto-commit: uncommitted changes at $TIMESTAMP"
fi
```

**Result**: Finalization now catches ALL uncommitted files automatically

## 🚨 NEW GATE ADDED: Essential Closure Notes Verification

**Issue**: Agents closing issues without proper documentation for future reference  
**Learning**: Future agents need implementation details, file locations, and integration guidance  
**Solution Implemented**: Added closure notes reminder gate in Finalization workflow

### 🔍 **Closure Notes Gate Added**

- **Location**: Step 5 - Issue Management section
- **Purpose**: Remind agents to add comprehensive closure notes
- **Template Provided**: Standard format for implementation details

### 📝 **Required Closure Notes Template**

```markdown
## Implementation Details & Documentation

### 📁 Files Created/Modified
- `path/to/file.py` - Brief description

### 🚀 Quick Start
```bash
# Example commands
python script.py --option value
```

### 📖 Key Documentation

- **Main Docs**: `path/to/README.md#section`
- **API Reference**: `path/to/api.md`

### 🔧 Integration Points

- How it connects to existing system
- Configuration requirements

### 📊 Production Features

- Key capabilities for production use
- Monitoring and performance characteristics

```

### ✅ **Finalization Enhancement Benefits**
1. **Future Agent Context**: Clear understanding of what was implemented
2. **Documentation Links**: Direct paths to relevant documentation
3. **Integration Guidance**: How to use and connect components
4. **Quick Start**: Immediate usage instructions (must include Beads Issue ID)
5. **Production Readiness**: Deployment and operational considerations

**Result**: Future agents can quickly understand and build upon previous work without digging through codebase

## 🚨 TOOLING FRICTION ALERT: Beads Closure Notes
**Issue**: Agents frequently hallucinate `bd note` which does not exist.
**Correct Command**: Use `bd comments add <issue-id> "<content>"` for final closure notes.
**Future Improvement**: An alias or new command `bd note` is under investigation in issue `agent-harness-4nb`.

## 🚨 NEW GATE ADDED: Mandatory Reflection Capture

**Issue**: Agents completing sessions without systematic learning capture  
**Learning**: Every session should capture learnings for continuous improvement  
**Solution Implemented**: Added mandatory reflection step in Finalization workflow

### 🔍 **Reflection Capture Gate Added**
- **Location**: Step 6 - Reflection Capture section
- **Purpose**: Automatically capture session learnings using reflect skill
- **Fallback**: Basic reflection template if skill unavailable
- **Priority**: Mandatory but non-blocking

### 🧪 **Reflection Capture Methods (in order of preference)**
1. **Reflect Skill**: `.agent/skills/reflect.sh`
2. **Reflect Script**: `.agent/scripts/reflect`  
3. **Python Fallback**: Automated basic reflection template
4. **Manual Reminder**: Instructions for manual capture

### 📝 **Fallback Reflection Template**
```python
reflection = {
    'timestamp': datetime.now().timestamp(),
    'mission_name': 'Session Work - Manual Reflection',
    'success_metrics': {
        'Work Completed': True,
        'Reflection Captured': False
    },
    'technical_learnings': [
        'Remember to use the reflect skill before RTB completion',
        'Systematic reflection ensures knowledge transfer'
    ],
    'challenges_overcome': [
        'Reflection skill not found - used fallback method'
    ],
    'quantitative_results': {
        'Files Changed': 'Unknown',
        'Session Duration': 'Unknown'
    },
    'next_mission_readiness': True,
    'mission_duration': 0.0,
    'status': 'PARTIAL'
}
```

### ✅ **Finalization Enhancement Benefits**

1. **Systematic Learning**: Every session captures knowledge automatically
2. **Continuous Improvement**: Built-in process for agent learning
3. **Knowledge Transfer**: Structured capture for future agents
4. **Quality Assurance**: Multiple fallback methods ensure reliability
5. **Process Consistency**: Standardized reflection format across all sessions

**Result**: Every Finalization will now capture learnings systematically, preventing knowledge loss

## 🚨 NEW GATE ADDED: Reflection Preview for Proactive Learning

**Issue**: Agents capturing learnings retrospectively instead of in real-time  
**Learning**: Better to know what to watch for during work, not discover it after  
**Solution Implemented**: Added reflection preview at Initialization for new work sessions

### 🎯 **Reflection Preview Gate Added**

- **Location**: Step 1.1 - Initialization Validation section
- **Trigger**: New work session (no git activity in past hour)
- **Purpose**: Prepare agents to capture friction points in real-time
- **Focus**: Proactive learning vs retrospective capture

### 📋 **What the Preview Shows**

**Key Areas to Watch During Work:**

1. **🔧 Tool/Process Friction**: Slow, buggy, or inefficient tools
2. **📝 Corrections**: Direct feedback and user corrections
3. **🎨 Preferences**: Coding style and architectural choices
4. **✅ Success Patterns**: Approaches that work particularly well
5. **🚫 Failures**: Mistakes and failed approaches
6. **🔄 Workarounds**: Temporary fixes and alternatives
7. **📊 Performance**: Bottlenecks and performance issues
8. **🤔 Confusion**: Unclear requirements or instructions
9. **🛑 Roadblocks**: Issues that completely stop progress

**Capture Strategy:**

- **✍️ Note friction AS THEY HAPPEN** (not retrospectively)
- **🏷️ Tag issues with severity levels**
- **📐 Record exact error messages and solutions**
- **⏰ Track time spent on different approaches**
- **🎯 Capture user preferences exactly**
- **🔗 Note dependencies and conflicts**

### 📝 **Friction Log Creation**

For new sessions, the system creates:

```markdown
# Session Friction Log - [timestamp]

## Quick Notes (add friction points as they happen)
- 
```

**Benefits:**

- **Real-time capture** vs memory-based recall
- **Structured format** for consistent documentation
- **Session context** preserved for later reflection
- **Friction patterns** easily identified over time

### 🎓 **Transformation in Agent Behavior**

**Before:**

```markdown
Agent works → Finalization → "What should I remember?" → Retroactive capture
```

**After:**

```markdown
Reflection preview → Agent watches for friction → Real-time notes → Finalization → Rich reflection data
```

### ✅ **Benefits of Proactive Reflection**

1. **🔍 Better Observation**: Agents actively watch for learning opportunities
2. **📊 Richer Data**: More detailed and accurate friction capture
3. **⚡ Real-time**: Capture insights when they're fresh
4. **🎯 Focused**: Know exactly what to pay attention to
5. **📈 Pattern Recognition**: Better identification of recurring issues
6. **🔄 Continuous Learning**: Every session contributes to system intelligence

**Result**: Agents now capture friction points in real-time with rich contextual data, dramatically improving reflection quality and system learning.

## Integration

This skill integrates with:

- Orchestrator Initialization/Finalization system
- Beads task management
- Multi-agent session locks
- Git workflow automation

## Troubleshooting

If Finalization fails:

1. Check for merge conflicts - resolve and retry
2. Verify network connectivity for git operations
3. Check beads daemon status (`bd daemon status`)
4. Review error logs in automation scripts
5. Manual intervention may be required for certain edge cases
