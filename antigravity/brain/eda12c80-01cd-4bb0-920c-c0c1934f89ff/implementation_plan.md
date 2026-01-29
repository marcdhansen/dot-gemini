# Upsert Notes and Repair Planning Files

This plan outlines the steps to take issues from `notes.md` and integrate them into the Beads issue tracker and relevant planning markdown files. It also includes maintenance for broken symlinks and missing project documentation.

## User Review Required

> [!IMPORTANT]
> Several global guidelines and manual files appear to be missing or have broken symlinks. I will attempt to reconstruct or placeholder them if they cannot be found.
> 
> [!NOTE]
> I will be creating new Beads issues manually by appending to `.beads/issues.jsonl`.

## Proposed Changes

### Maintenance: File Repair
- Check for differences between root and `LightRAG/` files for `final_report_BCBC.pdf` and other common files.
- Identify and address broken symlinks: `BEADS_FIELD_MANUAL.md`, `GLOBAL_AGENT_GUIDELINES.md`, `MODEL_PROFILING_RESULTS.md`, `SELF_EVOLUTION_GLOBAL.md`.

### [LightRAG] Documentation Updates
#### [MODIFY] [AGENT_INSTRUCTIONS.md](file:///Users/marchansen/claude_test/LightRAG/AGENT_INSTRUCTIONS.md)
- Add RAGAS summary (assessing graph retrieval).
- Add Langfuse summary (observability).
- Add ACE and MemEvolve GitHub links.

#### [MODIFY] [SELF_EVOLUTION.md](file:///Users/marchansen/claude_test/LightRAG/SELF_EVOLUTION.md)
- Add ACE and MemEvolve links to Learning Resources.
- Add research items: prompt tracking, MemGPT integration, Agentic RAG functionalities.
- Add backlog items for experiments (RAG modes) and features (Neo4j, Temporal, Self-healing).

#### [MODIFY] [TODO.md](file:///Users/marchansen/claude_test/LightRAG/TODO.md)
- Add maintenance task for file repair.
- Add evaluation experiments to backlog.

#### [MODIFY] [ROADMAP.md](file:///Users/marchansen/claude_test/LightRAG/ROADMAP.md)
- Update "Next Step" to reflect the new tasks from notes.

### Beads Issue Tracker
#### [MODIFY] [.beads/issues.jsonl](file:///Users/marchansen/claude_test/.beads/issues.jsonl)
- Manually append new issues extracted from `notes.md`.

## Verification Plan

### Automated Tests
- None applicable for these documentation-only changes.

### Manual Verification
- Verify that `bd list` (if run by user) shows the new issues.
- Inspect updated `.md` files to ensure formatting is correct and links are functional.
- Check symlinks in the root directory.
