# Task: Graph Reranking Implementation

## Pre-Flight Check (PFC)

- [x] Tool Check (bd, uv, markdownlint)
- [x] Context Check (ROADMAP.md, ImplementationPlan.md)
- [x] Status Check (bd ready)
- [x] Issue Check (bd show lightrag-bkj.4)
- [x] Flight Director PFC

## Research & Planning

- [x] Research existing retrieval and reranking logic in `lightrag/`
- [x] Create `implementation_plan.md` for Graph Reranking
- [x] Get user approval for the plan

## Implementation

- [x] Add `rerank_entities` and `rerank_relations` to `QueryParam`
- [x] Implement `rerank_graph_elements` in `operate.py`
- [x] Integrate graph reranking into `_build_query_context`
- [x] Document Speed-Accuracy Tradeoff in `docs/GRAPH_RERANKING.md`
- [x] Integrate mandatory latency rule into global `GEMINI.md`
- [x] Create `QualityAnalyst` skill for performance standards
- [x] Verify 'light' vs 'heavy' test suite categorization for benchmarking
- [x] Run Baseline evaluation
- [x] Run Scenario comparison (Ent, Rel, Both)

## Verification

- [x] Verify granular reranking toggles via server logs
- [x] Benchmarking results comparison (Baseline vs Scenarios)
- [x] Generate walkthrough report
