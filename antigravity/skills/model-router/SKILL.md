---
name: model-router
description: >
  Orchestrates specialised agent roles across different LLM models for
  optimised execution. Routes tasks to the model best suited for each role:
  strategy (Gemini), implementation (qwen2.5-coder), validation (Claude),
  and documentation search (GPT-4o-mini). Use when a task benefits from
  multiple specialist models working in sequence.
  Do NOT use for single-model tasks or when only one LLM is available.
compatibility: >
  Requires scripts/route_task.py and scripts/oracle_query.py in the skill
  directory. Each agent role requires its own API key and model access.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: multi-agent
  tags: [multi-model, orchestration, routing, specialised-agents, llm]
---

# Multi-Model Orchestrator Skill

**Purpose**: Orchestrate specialized agent roles across different LLM models for optimized execution.

## 🎭 Agent Roles (oh-my-opencode)

1. **Sisyphus (Lead)**: Strategy, task ledger management, and broad context handling. (Optimized for: Gemini 1.5 Pro)
2. **Hephaestus (Forge)**: High-speed code implementation and refactoring. (Optimized for: qwen2.5-coder)
3. **Oracle (Validator)**: Cross-check logic and security audit. (Optimized for: Claude 3.5 Sonnet)
4. **Librarian (Search)**: Documentation retrieval and knowledge base integration. (Optimized for: GPT-4o-mini)

## 🛠️ Usage

```bash
# Register a task for a specialized agent
python scripts/route_task.py --role hephaestus --task "Implement Pydantic schema"

# Get a multi-model opinion
python scripts/oracle_query.py --query "Is this refactoring safe?"
```

## 📜 Development Rules

- **Context-First**: Always provide role-specific context.
- **Synthesized Handoffs**: Never pass a raw prompt; synthesize previous agent's output.
- **Fail-Fast**: If an agent stalls, route back to Sisyphus for replanning.
