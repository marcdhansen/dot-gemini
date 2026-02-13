---
name: show-next-task
description: Shows what to work on next in the LightRAG project by running beads ready and providing intelligent recommendations
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# Show Next Task Skill

The `show-next-task` skill provides intelligent guidance on what to work on next in the LightRAG project. It answers the question "What should we work on next?" with actionable recommendations.

## Usage

```bash
/show-next-task
```

## Purpose

This skill performs comprehensive task analysis:

1. Runs `bd ready` to display all available tasks
2. Analyzes the task priority landscape (P0, P1, P2)
3. Indicates which tasks are currently in progress
4. Provides intelligent recommendations based on project impact
5. Reviews project roadmap for phase alignment opportunities
6. Suggests new feature development and issue creation to keep the plan moving
7. Offers concrete next steps to get started immediately

## Implementation

The skill executes:

```bash
./.agent/skills/show-next-task/scripts/next.sh
```

## Workflow Analysis

The script performs intelligent analysis:

1. **Task Discovery**: Captures full `bd ready` output
2. **Priority Classification**: Categorizes tasks by priority level
3. **Impact Assessment**: Provides recommendations based on:
   - **P0 Tasks**: Critical blockers requiring immediate attention
   - **P1 Tasks**: High-impact work with clear deliverables
   - **P2 Tasks**: Strategic work advancing project goals
   - **In Progress Tasks**: Work currently underway
4. **Roadmap Analysis**: Reviews current objectives and phase alignment
5. **Feature Development**: Suggests new issue creation and cross-linking opportunities
6. **Action Planning**: Suggests specific commands to get started

## Response Format

The skill delivers:

1. **Complete Task List**: Full `bd ready` output for context
2. **Priority Analysis**: Task count breakdown (P0: X, P1: Y, P2: Z)
3. **Intelligent Recommendations**: Priority-based guidance with reasoning
4. **Roadmap Analysis**: Current objectives, status, and phase alignment opportunities
5. **Feature Development Suggestions**: New issue creation and cross-linking recommendations
6. **Concrete Next Steps**: Specific `bd` commands and git workflow steps
7. **Project Context Links**: Implementation plan, documentation, and session status resources

## Decision Logic

**P0 PR Review Available**: Absolute top priority. Unblocking teammates is critical for project velocity.

- Recommendation: Review open PRs for P0 issues first.
- Reasoning: Blocks teammate progress and project merging.

**P0 Available**: Immediate attention required

- Recommendation: Start with P0 tasks first
- Reasoning: These are blocking project progress

**P1 Only**: High-priority work

- Recommendation: Tackle P1 tasks for maximum impact
- Reasoning: High importance with clear deliverables

**P2 Only**: Strategic development

- Recommendation: Work on P2 tasks systematically
- Reasoning: Advance project goals methodically

## Integration

This skill integrates with:

- **Beads Task Management**: `bd ready` command for task discovery
- **Project Roadmap**: `.agent/rules/ROADMAP.md` for phase alignment
- **Implementation Planning**: `.agent/rules/ImplementationPlan.md` for detailed guidance
- **LightRAG Protocols**: Project priorities and workflow standards
- **Agent Coordination**: Session status and multi-agent workflows
- **Git Operations**: Branch creation and task assignment workflows

## Example Output

```text
🎯 ALL Available Tasks in the LightRAG Project
=========================================================
📊 Task Priority Breakdown: P0: 1, P1: 2, P2: 7
🎯 HIGH PRIORITY (P1):
⚡ lightrag-abc: Implement feature X
🎯 Recommendation: Start with P0 tasks first - they are blocking project progress.
🚀 Next Steps: • Start recommended task: `bd start <task-id>`
🗺️ Roadmap Analysis & Feature Development:
📍 Current Focus: Phase 6: ACE Optimizer - Systematic prompt & curator refinement
📊 Status: ACTIVE
💡 Phase Alignment Opportunities: Consider creating supporting tasks for the next phase
🔗 Linking New Features to Ongoing Work: Review ImplementationPlan.md for detailed breakdown
🚀 New Feature Development Suggestions: Create integration testing and documentation tasks
📋 Keep the Plan Moving Forward: Create new issues with `bd create`
```

## Error Handling

The skill gracefully handles:

- Beads daemon not running
- No ready tasks available
- Command execution failures
- Network connectivity issues
