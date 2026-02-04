---
name: mission-briefing
description: Essential pre-mission briefing for agents with current status, protocol highlights, and friction areas to watch. Provides balanced overview without overwhelming details.
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# Mission Briefing Skill

Essential pre-mission information that prepares agents for successful task execution and learning capture.

## Usage

```bash
/mission-briefing
```

## Purpose

Provides balanced pre-mission briefing covering:
- **Current Status**: Git, issues, session locks
- **Protocol Highlights**: Quality gates, closure requirements, RTB blockers  
- **Friction Areas**: Tool friction, corrections, success patterns, failures
- **Common Pitfalls**: Mistakes to avoid based on past sessions
- **Session Checklist**: Quick reference for work session

## Implementation

The skill executes:

```bash
python .agent/skills/mission-briefing.py
```

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
- RTB blockers and requirements

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
- Pre-mission preparation
- During mission monitoring
- Pre-RTB completion
- Post-RTB verification

## Benefits

- **Time Efficient**: 2-3 minutes vs 10+ minutes for full RTB review
- **Focused Information**: Only what agents need, not implementation details
- **Proactive Learning**: Prepares agents to capture friction in real-time
- **Context Awareness**: Current status and session context
- **Error Prevention**: Highlights common mistakes to avoid

## Integration

This skill integrates with:
- **Beads**: Issue status and assignment tracking
- **Git**: Repository state and branch information  
- **Session Management**: Lock coordination with other agents
- **RTB Process**: Complements full return-to-base workflow
- **Reflection Skill**: Provides context for friction capture

## Workflow Integration

**Optimal Usage Pattern:**

1. **Start of Session**: `/mission-briefing` (2-3 minutes)
2. **During Work**: Real-time friction capture (guided by briefing)
3. **End of Session**: `/return-to-base` (full RTB execution)

This provides the perfect balance between:
- **Too Little Information** (just reflect skill)
- **Too Much Information** (full RTB protocol review)
- **Just Right** (mission briefing)

## Error Handling

If briefing fails:
1. Check git repository status
2. Verify beads availability
3. Check workspace directory structure
4. Review system permissions

## Advantages Over Alternatives

| Approach | Time | Information Quality | Practicality |
|-----------|-------|-------------------|--------------|
| Full RTB Review | 10-15 min | Implementation focus | Low |
| Just Reflect Skill | 2-3 min | Learning focus only | Medium |
| **Mission Briefing** | **2-3 min** | **Balanced** | **High** |

The mission briefing hits the sweet spot: comprehensive enough for context, focused enough for efficiency, practical enough for daily use.