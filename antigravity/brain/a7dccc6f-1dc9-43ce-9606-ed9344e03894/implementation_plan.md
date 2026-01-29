# Core Stability Verification & Local Reranker Finalization

This plan addresses the P0 task of verifying system stability with the BCBC PDF and the P1 task of completing the local reranker integration.

## Proposed Changes

### [LightRAG Core]

#### [MODIFY] [rerank.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/rerank.py)
- Ensure `local_rerank` is robust and properly handles missing dependencies.
- (Optional) Export `local_rerank` if needed for cleaner imports.

### [Tests]

#### [MODIFY] [test_local_reranker.py](file:///Users/marchansen/claude_test/LightRAG/tests/test_local_reranker.py)
- Update test to correctly import `local_rerank` and perform a basic functional check.

## Verification Plan

### Automated Tests
1. **Core Stability (P0)**:
   - Run a script to ingest `final_report_BCBC.pdf`.
   - Run a set of queries against the ingested data to verify retrieval and generation.
   - Command: `cd LightRAG && uv run start_bcbc_eval.py` (Assuming this script is for this purpose, need to check it first).
2. **Local Reranker (P1)**:
   - Install `FlagEmbedding`: `uv pip install FlagEmbedding`.
   - Run the dedicated test: `cd LightRAG && pytest tests/test_local_reranker.py`.

### Manual Verification
- Check the generated graph in the WebUI (if possible, though I'm an agent).
- Verify logs for any errors during ingestion.
