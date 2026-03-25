---
name: initialization-briefing
description: Essential pre-session briefing for agents with current status, protocol highlights, and friction areas to watch. Provides balanced overview without overwhelming details.
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# Initialization Briefing Skill

Essential pre-session information that prepares agents for successful task execution and learning capture.

## Usage

```bash
/initialization-briefing
```

## Purpose

Provides balanced pre-initialization briefing covering:

- **Current Status**: Git, issues, session locks
- **Protocol Highlights**: Quality gates, closure requirements, Finalization blockers  
- **Friction Areas**: Tool friction, corrections, success patterns, failures
- **Common Pitfalls**: Mistakes to avoid based on past sessions
- **Session Checklist**: Quick reference for work session

## Implementation

The skill executes:

```bash
python ~/.gemini/antigravity/skills/initialization-briefing/initialization_briefing.py
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
- **TDD Violations**: Writing tests AFTER implementation (run `tdd-check` first!)

### 5. Mode Selection: Turbo vs Full SOP

| Mode | Use When | TDD |
|------|----------|-----|
| **Turbo** | Internal tools, quick fixes, ad-hoc | Minimal/stub |
| **Full SOP** | Features, external-facing, multi-session | Full TDD |

**Turbo indicators:** Internal tooling, single session, no external users
**Full SOP indicators:** User-facing, needs planning, >1 session

### 6. TDD Enforcement

**Before writing any code, run TDD check:**

```bash
tdd-check src/agent_harness/new_module.py
```

**Progressive Disclosure by Task Size:**

| Complexity | Time | Requirement |
|------------|------|-------------|
| Trivial | <5 min | Exempt (`--exempt --reason`) |
| Small | 5-30 min | Test stub (`tdd-check` prompts) |
| Medium+ | >30 min | Full TDD (Red→Green→Refactor) |

**Quick Fixes:** Use exemption to avoid TDD fatigue:
```bash
tdd-check <file> --exempt --reason "Config only"
```

### 6. Session Phase Tracking (NEW)

**Track progress with these commands:**

```bash
# Check current phase status
session-status

# Mark a phase complete
phase-complete 3_planning --notes "Blast radius done"
phase-complete 4_execution --notes "Implementation complete"
```

**Required phases by mode:**

| Mode | Required Phases |
|------|----------------|
| Turbo | 5, 6, 7 (skip 1-4) |
| Full | 1, 2, 3, 4, 5, 6, 7 |

### 7. Session Checklist

- Pre-session preparation
- During session monitoring
- Pre-Finalization completion
- Post-Finalization verification

## Benefits

- **Time Efficient**: 2-3 minutes vs 10+ minutes for full Finalization review
- **Focused Information**: Only what agents need, not implementation details
- **Proactive Learning**: Prepares agents to capture friction in real-time
- **Context Awareness**: Current status and session context
- **Error Prevention**: Highlights common mistakes to avoid

## Integration

This skill integrates with:

- **Beads**: Issue status and assignment tracking
- **Git**: Repository state and branch information  
- **Session Management**: Lock coordination with other agents
- **Finalization Process**: Complements full Finalization workflow
- **Reflection Skill**: Provides context for friction capture

## Workflow Integration

**Optimal Usage Pattern:**

1. **Start of Session**: `/initialization-briefing` (2-3 minutes)
2. **During Work**: Real-time friction capture (guided by briefing)
3. **End of Session**: `/finalization` (full Finalization execution)

This provides the perfect balance between:

- **Too Little Information** (just reflect skill)
- **Too Much Information** (full Finalization protocol review)
- **Just Right** (initialization briefing)

## Error Handling

If briefing fails:

1. Check git repository status
2. Verify beads availability
3. Check workspace directory structure
4. Review system permissions

## Advantages Over Alternatives

| Approach | Time | Information Quality | Practicality |
| :--- | :--- | :--- | :--- |
| Full Finalization Review | 10-15 min | Implementation focus | Low |
| Just Reflect Skill | 2-3 min | Learning focus only | Medium |
| **Initialization Briefing** | **2-3 min** | **Balanced** | **High** |

The initialization briefing hits the sweet spot: comprehensive enough for context, focused enough for efficiency, practical enough for daily use.
