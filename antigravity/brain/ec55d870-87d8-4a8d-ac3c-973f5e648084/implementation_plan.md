# Graph Reranking Implementation

Implement performance-focused graph reranking for entities and relationships to improve retrieval quality in Knowledge Graph RAG modes.

## User Review Required

> [!IMPORTANT]
> This change introduces reranking for graph elements (entities and relations). While it is controlled by the existing `enable_rerank` flag, it will increase the number of reranker API calls (or local model inferences) per query.
>
> - One call for entities (if `mode` includes local/hybrid/mix)
> - One call for relations (if `mode` includes global/hybrid/mix)
> - Existing call for text chunks remains.

## Proposed Changes

### Core Retrieval Logic

#### [MODIFY] [operate.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/operate.py)

- Implement `rerank_graph_elements` helper function:
  - Accepts a list of entities or relationships.
  - Formats them into strings (e.g., `"Entity: <name> | Description: <desc>"`).
  - Calls the configured reranker via `apply_rerank_if_enabled`.
  - Updates the objects with `rerank_score` and sorts them.
- Update `QueryParam` in [base.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/base.py):
  - Add `rerank_entities: bool = True`
  - Add `rerank_relations: bool = True`
- Update `_build_query_context` in [operate.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/operate.py):
  - Insert a new stage between **Stage 1 (Search)** and **Stage 2 (Truncation)**.
  - Call `rerank_graph_elements` for entities if `query_param.enable_rerank` AND `query_param.rerank_entities` are True.
  - Call `rerank_graph_elements` for relations if `query_param.enable_rerank` AND `query_param.rerank_relations` are True.
- Update `_apply_token_truncation`:
  - Ensure it respects the new order established by the reranker.

---

## Benchmarking Reranking

To compare the impact of reranking, we will use the existing Ragas evaluation framework.

### Metrics to Track

The primary metric affected by reranking is **Context Precision** (measuring how high the relevant information is ranked in the retrieved context). Improvements in Context Precision typically lead to better **Faithfulness** and **Answer Relevance**.

### Comparison Methodology

1. **Baseline Run**: Run `eval_rag_quality.py` with the current code (reranking only applied to chunks).
2. **Implementation Run (Scenarios)**:
    - **Scenario A (Entities Only)**: `rerank_entities=True`, `rerank_relations=False`.
    - **Scenario B (Relations Only)**: `rerank_entities=False`, `rerank_relations=True`.
    - **Scenario C (Full Graph)**: `rerank_entities=True`, `rerank_relations=True`.
3. **A/B Test**: Toggle the `enable_rerank` flag in `QueryParam` during evaluation to compare:
    - **No Rerank**: `enable_rerank=False`
    - **Existing (Chunk only)**: Current implementation.
    - **Full (Graph + Chunk)**: New implementation.

### Datasets

- `hotpotqa_sample.json`: For general multi-hop reasoning.
- `bcbc_testset.json`: For document-specific evaluation.

---

## Verification Plan

### Automated Tests

- Create `tests/test_graph_reranking.py`:
  - Mock `reranker` to return specific scores.
  - Verify that entities with higher rerank scores (but lower initial cosine similarity) are kept after token truncation.
  - Verify that relationships are similarly prioritized.
- Run existing reranker tests:

  ```bash
  pytest tests/test_local_reranker.py tests/test_rerank_chunking.py
  ```

### Manual Verification

- Start LightRAG server with a local reranker (e.g., `BAAI/bge-reranker-v2-m3`).
- Perform queries and check logs to verify the reranking step is being called for entities/relations.
- Observe the `Final chunks S+F/O` log to see if the source elements changed due to reranking.
