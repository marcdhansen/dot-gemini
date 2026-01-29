�# 🗺️ Project Roadmap & Navigation: LightRAG

This is the central directory for all project-specific planning, tracking, and instruction documents.

## 🎯 Current Objective

- **Task**: Infrastructure & Process Improvements (Flight Director, YAML-default)
- **Status**: ACTIVE
- **Result**: Robust automated checks and optimized extraction paths.
- **Next Step**: Phase 6: ACE Optimizer - Systematic prompt refinement.

## 🚀 Active Work

- **[Implementation Plan](ImplementationPlan.md)**: Detailed technical breakdown of current and upcoming phases.
- **[Task Tracker (Beads)](https://github.com/steveyegge/beads)**: Absolute source of truth for Project Tasks (`bd list`).

## 🧠 Project Context & Evolution

- **[Model Profiling Results](../../MODEL_PROFILING_RESULTS.md)**: Benchmarks for the specific models used in this repo.

## 📖 Instructions & Guides (Local)

- **[Project README](../../README.md)**: Main project documentation.
- **[Observability & Langfuse](../../docs/OBSERVABILITY.md)**: Setup and benefits of Langfuse tracing.
- **[Evaluation & RAGAS](../../docs/EVALUATION.md)**: How to run and interpret RAGAS benchmarks.
- **[ACE Framework](../../docs/ACE_FRAMEWORK.md)**: High-level overview of Agentic Context Evolution.
- **[Local Setup Hints](../../docs/local_setup_hints.md)**: specific commands for manual testing.
- **[Frontend Build Guide](../../docs/FrontendBuildGuide.md)**: Instructions for building the WebUI.
- **[Docker Deployment](../../docs/DockerDeployment.md)**: Guide for containerized setup.

## 🌐 Global Resources

- **[Global Agent Guidelines](../../global_docs/GEMINI.md)**: **MANDATORY** PFC, LTP, and 3-Tier Strategy.
- **[Global Self-Evolution](../../global_docs/SELF_EVOLUTION_GLOBAL.md)**: Universal agent behavioral patterns.
- **[Beads Field Manual](../../global_docs/HOW_TO_USE_BEADS.md)**: Global guide for using the Beads system.

## 📈 Recent Accomplishments

- ✓ **Type Safety Refactoring** (2026-01-28): Resolved critical Pyright errors across
  core modules and relaxed graph data types for better compatibility (lightrag-3mc).
- ✓ **ACE Phase 5: Curator** (2026-01-27): Implemented automated graph repair
  (deletion, merging) and integrated into ACE query loop.
- ✓ **ACE Asymmetric Routing** (2026-01-27): Implemented model-specific routing
  for extraction vs. reflection (lightrag-043).
- ✓ **Librarian Cross-Reference** (2026-01-29): Implemented `scripts/check_docs_coverage.py`,
  resolved all orphaned documentation, and integrated checks into `pre-commit`
  and Flight Director (lightrag-6l3).
- ✓ **Documentation Validator** (2026-01-27): Created `scripts/validate_docs.py`
  to ensure `ARCHITECTURE.md` integrity (lightrag-rxg).
- ✓ **Gold Standard Tests** (2026-01-27): Implemented `tests/test_gold_standard_extraction.py`
  validating extraction quality with pass/fail thresholds (lightrag-d9h).
- ✓ **Graph Visualization** (2026-01-27): Implemented `GraphControl` with
  `useLightragGraph` and integrated Sigma.js for knowledge graph inspection.
- ✓ **ACE Phase 3** (2026-01-27): Finalized minimal ACE framework prototype
  (Generator/Reflector/Curator stubs).
- ✓ **Graph Reranking Implementation** (2026-01-27): Implemented `rerank_entities`
  and `rerank_relations` toggles, integrated into context building, and
  benchmarked with Ragas (+13.8% boost).
- ✓ **Evaluation & Testing Standardization** (2026-01-26): Implemented tiered
  testing (Light/Heavy), integrated Langfuse, and created documentation for
  RAGAS and ACE.
- ✓ **Refactor Project Structure** (2026-01-26): Cleaned up workspace, moved docs,
  created global symlinks.
- ✓ **ACE Minimal Prototype** (2026-01-22): Implemented and verified the Core
  Loop (Generate-Reflect-Curate).
- ✓ **Ragas Compatibility Fix** (2026-01-22): Resolved `TypeError` in Ragas 0.4.3
  using Legacy wrappers.
- ✓ **Baseline RAGAS Evaluation** (2026-01-22): Preliminary pass successful.

---
Last Updated: 2026-01-28
�"(c927de12a977efdff810173207b1be81e2e7d4e02Nfile:///Users/marchansen/antigravity_lightrag/LightRAG/.agent/rules/ROADMAP.md:6file:///Users/marchansen/antigravity_lightrag/LightRAG