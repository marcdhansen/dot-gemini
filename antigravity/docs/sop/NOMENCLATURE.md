# Session Terminology Reference

This document defines the standard terminology used in the Universal Agent Protocol (SOP), providing consistent language for session-based development workflows.

## Core Phases

- **Initialization**: Environment setup, tool verification, and readiness checks before starting a task.
- **Execution**: The core development loop, implementing features using TDD.
- **Finalization**: Quality gates, linting, testing, and synchronization with the remote repository.
- **Standard Operating Procedure (SOP)**: The authoritative workflow governing agent behavior from initialization to clean state.
- **Retrospective**: Strategic analysis phase after finalization for capturing learnings and friction.
- **Wrap This Up (WTU)**: A trigger to run final compliance checks (Finalization/Retrospective) before ending the session.

## Key Roles & Concepts

- **Orchestrator**: The central system skill that validates SOP compliance and gates phase transitions.
- **Session**: A single operational cycle of an agent working on a task.
- **Task**: A specific unit of work associated with a Beads issue.
- **Quality Gate**: Automated validation (tests, linting) that must pass before finalization is considered complete.
- **Friction Log**: A real-time record of tool, process, or workflow issues encountered during a session.

## Strategic Context

- **Roadmap**: The high-level plan and backlog of work items.
- **Implementation Plan**: The specific technical design and blast radius analysis for a task.
- **Collaboration**: Strategies for multi-agent coordination and concurrent workflows.

## Usage

- "Starting **Initialization** for task #123."
- "Moving to **Execution** phase."
- "Beginning **Finalization**; running quality gates."
- "Running **Retrospective** to capture friction points."
- "Consulting the **Orchestrator** for protocol compliance."
- "Starting a new **Session** for the next task."
- "**WTU** - let's run the **Finalization** checklist."
