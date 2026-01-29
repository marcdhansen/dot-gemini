# Document Migration & Consolidation Plan (Antigravity Standards)

This plan ensures all project and global documentation is stored in the correct locations according to Google Antigravity standards.

## Proposed Changes

### Global Configuration (`~/.gemini/`)

#### [MODIFY] [GEMINI.md](file:///Users/marchansen/.gemini/GEMINI.md)
- Consolidate all global operational rules into this file:
    - PFC (Pre-Flight Check)
    - LTP (Landing the Plane)
    - 3-Tier Planning Strategy
    - Beads Field Manual integration
    - Global Self-Evolution Strategy
- This becomes the definitive source of truth for global agent behavior.

#### [DELETE] [GLOBAL_AGENT_GUIDELINES.md](file:///Users/marchansen/.gemini/GLOBAL_AGENT_GUIDELINES.md)
#### [DELETE] [BEADS_FIELD_MANUAL.md](file:///Users/marchansen/.gemini/BEADS_FIELD_MANUAL.md)
#### [DELETE] [SELF_EVOLUTION_GLOBAL.md](file:///Users/marchansen/.gemini/SELF_EVOLUTION_GLOBAL.md)
#### [DELETE] [AGENTS.md](file:///Users/marchansen/.gemini/AGENTS.md)

### Project Root (`/Users/marchansen/claude_test/`)

#### [NEW] [.agent/rules/](file:///Users/marchansen/claude_test/.agent/rules/)
Move all project-specific "rules" and context here:
- **[AGENT_INSTRUCTIONS.md](file:///Users/marchansen/claude_test/.agent/rules/AGENT_INSTRUCTIONS.md)**: Project-specific technical guides.
- **[ROADMAP.md](file:///Users/marchansen/claude_test/.agent/rules/ROADMAP.md)**: Current objective and status.
- **[ImplementationPlan.md](file:///Users/marchansen/claude_test/.agent/rules/ImplementationPlan.md)**: Technical execution plan.
- **[SELF_EVOLUTION.md](file:///Users/marchansen/claude_test/.agent/rules/SELF_EVOLUTION.md)**: Project-specific learning.
- **[MODEL_PROFILING_RESULTS.md](file:///Users/marchansen/claude_test/.agent/rules/MODEL_PROFILING_RESULTS.md)**: Local benchmarks.
- **[ACE_PROTOTYPE.md](file:///Users/marchansen/claude_test/.agent/rules/ACE_PROTOTYPE.md)**: [MOVE from LightRAG/docs/] ACE architecture details.
- **[DEVELOPER_LEARNINGS.md](file:///Users/marchansen/claude_test/.agent/rules/DEVELOPER_LEARNINGS.md)**: [MOVE from LightRAG/docs/] Technical findings.
- **[Research PDFs](file:///Users/marchansen/claude_test/.agent/rules/)**: [MOVE from root] ACE Summary, MemEvolve Paper, etc.
- **[GLOBAL_AGENT_GUIDELINES.md](file:///Users/marchansen/claude_test/.agent/rules/GLOBAL_AGENT_GUIDELINES.md)** (Pointer): Link to global `~/.gemini/GEMINI.md`.
- **[BEADS_FIELD_MANUAL.md](file:///Users/marchansen/claude_test/.agent/rules/BEADS_FIELD_MANUAL.md)** (Pointer): Link to global `~/.gemini/GEMINI.md`.
- **[AGENTS.md](file:///Users/marchansen/claude_test/.agent/rules/AGENTS.md)** (Pointer): Link to global `~/.gemini/GEMINI.md`.

#### [NEW] [.agent/workflows/](file:///Users/marchansen/claude_test/.agent/workflows/)
Check and move any workflow-related files here.

### Cleanup
Remove temporary files and original root-level `.md` files once moved.

## Verification Plan
1. Check that `~/.gemini/GEMINI.md` contains all global rules.
2. Confirm `.agent/rules/` contains all project documentation.
3. Verify that all links in `ROADMAP.md` (now in `.agent/rules/`) are updated to point to the correct relative paths.
