---
name: retrospective
description: Post-session strategic analysis invoked after Finalization. Synthesizes session results, reflection learnings, and generates improvement suggestions for SOP and workflow optimization.
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

# Retrospective (Finalization Session Analysis) Skill

**Separate phase** after Finalization for strategic learning and session closure.

## Usage

```bash
/retrospective
python ~/.gemini/antigravity/skills/retrospective/scripts/finalization_debriefing.py
```

## Workflow

```mermaid
graph LR
    A[Initialization] --> B[Work]
    B --> C[Finalization]
    C --> D[Retrospective]
    D --> E[Session End]
```

**Finalization** = Safe landing (quality gates, git, PR)  
**Retrospective** = Strategic learning (reflect, handoff, analysis)

## Finalization Debriefing Steps

### 1. Reflect

Invoke `/reflect` to:

- Capture learnings, preferences, and friction
- Update SKILL.md files ("correct once, never again")
- Answer strategic questions (cognitive load, design patterns)

### 2. Handoff

Provide summary of:

- Work completed and deliverables
- Beads issues created/closed
- Skills used
- Recommended next steps

### 3. Plan Cleanup

Clear the `## Approval` marker in task.md to prevent accidental auto-starts.

### 4. Strategic Analysis

Run `finalization_debriefing.py` to generate:

- Session summary and git activity
- Friction reduction opportunities
- Efficiency improvements (project and SOP level)
- Agentic design patterns for multi-agent collaboration

### 5. Orchestrator Verification

```bash
python ~/.gemini/antigravity/skills/Orchestrator/scripts/check_protocol_compliance.py --retrospective
```

Verifies:

- ✅ Reflection captured
- ✅ Debrief file generated
- ✅ Plan approval cleared

## Output

Debrief saved to: `~/.gemini/antigravity/brain/{session-id}/debrief.md`

## Strategic Questions

During reflection, address:

1. **Cognitive Load**: "Are there parts of the SOP where the agent's cognitive load could be reduced by using scripts?"
2. **Design Patterns**: "Identify design patterns and recommended refactoring strategies."
3. **Multi-Agent**: "What improvements could enhance parallel agent workflows?"

## Integration

- **Finalization**: Runs after Finalization completion
- **Reflect**: Integrated as first debrief step
- **Orchestrator**: Verified via `--retrospective` flag
