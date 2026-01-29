# Walkthrough - Upsert Notes & File Alignment

I have successfully upserted the issues from `notes.md` into the Beads issue tracker and updated the planning markdown files. I also performed critical maintenance on the project's file structure.

## Summary of Changes

### 1. File Alignment & Persistence
- **Flipped Symlinks**: I reversed the symbolic link direction for all core planning files. The root directory is now the **source of truth** for these files, and `LightRAG/` contains symlinks pointing to the root. This prevents accidental overwrites or deletions during `git pull` operations within the `LightRAG` repository.
    - Updated files: `AGENTS.md`, `AGENT_INSTRUCTIONS.md`, `FEEDBACK.md`, `ImplementationPlan.md`, `ROADMAP.md`, `SELF_EVOLUTION.md`, `TODO.md`.
- **Restored Missing Files**: I identified and restored placeholders for four "Global" documentation files that had broken symlinks:
    - `BEADS_FIELD_MANUAL.md`
    - `GLOBAL_AGENT_GUIDELINES.md`
    - `MODEL_PROFILING_RESULTS.md`
    - `SELF_EVOLUTION_GLOBAL.md`

### 2. Documentation Updates
- **[AGENT_INSTRUCTIONS.md](file:///Users/marchansen/claude_test/AGENT_INSTRUCTIONS.md)**:
    - Added detailed summaries for **RAGAS** (assessing graph retrieval) and **Langfuse** (observability).
    - Included links to **ACE** and **MemEvolve** GitHub repositories.
- **[SELF_EVOLUTION.md](file:///Users/marchansen/claude_test/SELF_EVOLUTION.md)**:
    - Added research items for **Prompt Tracking** and **MemGPT/Letta** integration.
    - Added a **Technical Experiments Backlog** for RAG modes, advanced chunking, and additional graph storage support (Neo4j).
- **[TODO.md](file:///Users/marchansen/claude_test/TODO.md)**:
    - Added maintenance and evaluation tasks to the project backlog.
- **[ROADMAP.md](file:///Users/marchansen/claude_test/ROADMAP.md)**:
    - Updated "Next Steps" to include technical experiments and Neo4j integration.
    - Fixed relative links to global resources.

### 3. Beads Issue Tracker
I created **8 new issues** in the Beads tracker to ensure the ideas from `notes.md` are documented and trackable:
- `lightrag-taw`: Investigate Agent Prompt tracking solution
- `lightrag-vc3`: Evaluate MemGPT/Letta integration
- `lightrag-t4x`: Verify ACE repo tests on LightRAG
- `lightrag-atb`: Research Agentic RAG functionalities
- `lightrag-t1m`: Benchmark RAG modes
- `lightrag-c9d`: Experiment with advanced chunking
- `lightrag-fqq`: Neo4j/Temporal Graph support
- `lightrag-55x`: Self-healing & n8n harness review

## Verification Results

### Symlink Structure
```bash
ls -l LightRAG/*.md
# Results show all .md files (except READMEs/SECURITY/notes) are symlinked to ../FILE.md
```

### Beads Issues
```bash
bd list --limit 8 --sort created -r
# Confirms the 8 new lightrag-xxx issues exist.
```

### Content Validation
I've manually verified the content of `AGENT_INSTRUCTIONS.md` and `SELF_EVOLUTION.md` to ensure the new information is correctly formatted and added to the appropriate sections.
