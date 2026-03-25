---
name: session-briefing
description: >
  Essential pre-session briefing for agents with current project status,
  protocol highlights, and friction areas to watch. Use when starting a
  new session to orient the agent before any work begins, or when the
  agent needs a lightweight status refresh at session start.
  Do NOT use mid-session; invoke only at session start.
compatibility: >
  Requires Python 3.x and Read access to project files. Script at
  ~/.gemini/antigravity/skills/session-briefing/initialization_briefing.py.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: session-management
  tags: [initialization, briefing, session-start, orientation, sop]
  disable-model-invocation: true
  allowed-tools: Bash, Read, Glob, Grep
---

# Initialization Briefing Skill

Essential pre-session information that prepares agents for successful task execution and learning capture.

## Usage

```bash
/initialization-briefing
```

Or directly:

```bash
python ~/.gemini/antigravity/skills/session-briefing/initialization_briefing.py
```

### Command-Line Options

| Option | Description |
| :--- | :--- |
| `--turbo` | Run in Turbo Mode (lightweight, skips protocol details) |
| `--force-full` | Force Full Mode regardless of task type |
| `--clear-cache` | Clear static content cache |

## Briefing Modes

The skill operates in three modes:

| Mode | Trigger | Content |
| :--- | :--- | :--- |
| **Ultra-Lite** | Admin task detected | Current status only |
| **Turbo** | `--turbo` flag + no code changes | Status + PRs + minimal info |
| **Full** | Code changes detected | All sections |

### Ultra-Lite Mode

Automatically activates for administrative/non-implementation tasks. Detects task type by checking:

- Command-line arguments (keywords: beads, bd, issue, q&a, docs, research, help, etc.)
- Beads issue description
- Task context files

Displays only current status - no protocol details.

### Turbo Mode

Lightweight mode for quick sessions:

- Shows current status, PRs, and Beads pr:open issues
- Skips protocol highlights, friction areas, pitfalls, checklist
- Escalates to Full Mode if code changes are detected

### Full Mode

Complete briefing for implementation work:

- All status checks (Git, Beads, PRs)
- Protocol highlights and quality gates
- Areas to watch for friction capture
- Common pitfalls to avoid
- Session checklist

## Purpose

Provides balanced pre-initialization briefing covering:

- **Current Status**: Git, issues, session locks
- **Protocol Highlights**: Quality gates, closure requirements, Finalization blockers  
- **Friction Areas**: Tool friction, corrections, success patterns, failures
- **Common Pitfalls**: Mistakes to avoid based on past sessions
- **Session Checklist**: Quick reference for work session

## Implementation

### Optimizations

1. **Parallel Execution**: Git status, PRs, and Beads data fetched concurrently using ThreadPoolExecutor
2. **Static Content Caching**: Protocol details cached in `.agent/.briefing_cache/` for 1 hour
3. **Fast Git Checks**: Uses `git diff --quiet` for quick yes/no detection
4. **Admin Task Detection**: Auto-detects administrative tasks for minimal briefing

## Briefing Sections

### 1. Current Status Check

- Git state (clean/dirty, branch info)
- Active beads issues (in-progress)
- Session locks (other active agents)
- Workspace validation

### 2. Protocol Highlights  

- Quality gates (tests, linting, type checking)
- Closure requirements (file locations, quick start, docs)
- Learning capture expectations
- Finalization blockers and requirements

### 3. Areas to Watch

- **Tool/Process Friction**: Slow/buggy tools, inefficient workflows
- **Corrections & Preferences**: User feedback, coding style, architecture
- **Success Patterns**: Effective approaches and solutions
- **Failures & Challenges**: Mistakes, dead ends, configuration issues
- **Workarounds & Performance**: Temporary fixes, bottlenecks, resource issues

### 4. Common Pitfalls

- Documentation mistakes (missing closure notes, no quick start)
- Quality gate issues (skipping tests, duplicate markdown files)
- Git & workflow errors (unpushed changes, branch cleanup)
- Learning & reflection mistakes (retrospective vs real-time capture)

### 5. Session Checklist

- Pre-session preparation
- During session monitoring
- Pre-Finalization completion
- Post-Finalization verification

## Benefits

- **Time Efficient**: Ultra-Lite: ~5 seconds, Turbo: ~10 seconds, Full: ~15 seconds
- **Adaptive**: Automatically adjusts briefing depth based on task type
- **Focused Information**: Only what agents need, not implementation details
- **Proactive Learning**: Prepares agents to capture friction in real-time
- **Context Awareness**: Current status and session context
- **Error Prevention**: Highlights common mistakes to avoid

## Integration

This skill integrates with:

- **Beads**: Issue status and assignment tracking
- **Git**: Repository state and branch information  
- **GitHub**: PR status and review requirements
- **Session Management**: Lock coordination with other agents
- **Finalization Process**: Complements full Finalization workflow
- **Reflection Skill**: Provides context for friction capture

## Workflow Integration

**Optimal Usage Pattern:**

1. **Start of Session**: `/initialization-briefing` (auto-detects appropriate mode)
2. **During Work**: Real-time friction capture (guided by briefing)
3. **End of Session**: `/finalization` (full Finalization execution)

This provides the perfect balance between:

- **Too Little Information** (just reflect skill)
- **Too Much Information** (full Finalization protocol review)
- **Just Right** (initialization briefing)

## Error Handling

If briefing fails:

1. Check git repository status
2. Verify beads/gh availability
3. Check workspace directory structure
4. Review system permissions
5. Try `--clear-cache` if caching issues suspected

## Advantages Over Alternatives

| Approach | Time | Information Quality | Practicality |
| :--- | :--- | :--- | :--- |
| Full Finalization Review | 10-15 min | Implementation focus | Low |
| Just Reflect Skill | 2-3 min | Learning focus only | Medium |
| **Initialization Briefing** | **5-15 sec** | **Adaptive** | **High** |

The initialization briefing hits the sweet spot: comprehensive enough for context, focused enough for efficiency, practical enough for daily use.
