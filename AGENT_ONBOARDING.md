# 🚀 Agent Onboarding & Standard Mission Protocol (SMP)

To initialize this project in a new environment or with a new agent (e.g., OpenCode, Claude CLI), follow these steps:

1. **Read the Bootstrap Guide**: Immediately read `.agent/BOOTSTRAP.md` to understand project-specific initialization.
2. **Run the Bootstrap Script**: Execute `./scripts/agent-init.sh` to automatically verify your toolchain and get up to speed on the mission state.

## 1. Anchor to Global Memory

Identify the global configuration directories.
> "Read the Global Agent Rules in `~/.gemini/GEMINI.md` and follow the Standard Mission Protocol (SMP). Use the Global Index at `~/.gemini/GLOBAL_INDEX.md` as your primary navigation map."

## 2. Verify Tool Availability

Confirm the core toolchain is accessible:

```bash
which bd uv python git
```

*If `bd` is missing, run `bd onboard` or follow the guide in `~/.gemini/HOW_TO_USE_BEADS.md`.*

## 3. Initialize Mission Readiness (PFC)

Run the **Pre-Flight Check (PFC)** to align with the current project state:

```bash
python ~/.gemini/antigravity/skills/FlightDirector/scripts/check_flight_readiness.py --pfc
```

### ⚡ Turbo-Bootstrap (Recommended)

You can automate steps 2-4 by running the initialization script:

```bash
./scripts/agent-init.sh
```

## 4. Connect to Project Brain

Read the following files to understand the mission status:

1. `.agent/rules/ROADMAP.md`: High-level navigation.
2. `.agent/rules/ImplementationPlan.md`: Technical breakdown.
3. Execute `bd ready`: To see current unblocked tasks.

## 5. Standard Mission Loop (RTB)

You MUST execute the **Return To Base (RTB)** procedure before ending your session:

1. Run project-specific linters/tests.
2. Update/Close Beads issues.
3. Execute `/reflect` to save session learnings to `~/.gemini/GEMINI.md`.
4. Run `bd sync` and `git push`.

## 6. Long-Term Memory (Automem)

This project uses **Automem** for graph+vector long-term memory across sessions.

1. **Initialize Automem**: If not already running, navigate to `~/GitHub/verygoodplugins/automem` and run `make dev`.
2. **Contextual Awareness**: Query Automem at the start of a session for relevant patterns, preferences, and session-spanning context.
3. **Capture**: Ensure significant session learnings are stored in Automem during the `/reflect` phase.

## 7. Observability (Langfuse)

This project uses **Langfuse** for tracing LLM calls and RAGAS evaluations.

1. **Local Langfuse**: Ensure a local Langfuse instance is accessible (usually via Docker).
2. **Verification**: After running any query, check for new traces in Langfuse to ensure observability is operational.
