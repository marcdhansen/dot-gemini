# Task: Immediate Maintenance & Fixes

- [x] **Fix Ragas Deprecation Warning** <!-- id: 8 -->
    - [x] Update imports in `eval_rag_quality.py` to use `ragas.metrics.collections`
    - [x] Verify fix
- [x] **Fix Reranking Warning** <!-- id: LightRAG-o5v -->
    - [x] Disable rerank in client (eval_rag_quality.py) to match server config
    - [x] Integrate local Ollama reranker (FlagEmbedding)
    - [x] Fix RAGAS metric initialization in eval script
    - [x] Increase evaluation query timeouts and add Ragas RunConfig
    - [x] Fix 404 error by adding native Ollama embedding support
    - [x] Verify reranking impact via comparison script
    - [x] Final verification with full evaluation run

# Completed Tasks (BCBC Evaluation)
- [x] Check system configuration (timeouts, models) <!-- id: 0 -->
- [x] Ensure LightRAG server is running <!-- id: 1 -->
- [x] Ingest `final_report_BCBC.pdf` <!-- id: 2 -->
- [x] Monitor logs for errors or timeouts <!-- id: 3 -->
- [x] Verify graph creation and node count <!-- id: 4 -->
- [x] **Generate BCBC Test Dataset** <!-- id: 6 -->
    - [x] Extract text from PDF
    - [x] Generate QA pairs using LLM
    - [x] Save as `bcbc_testset.json`
- [x] **Run Ragas Evaluation** <!-- id: 7 -->
    - [x] Execute `eval_rag_quality.py` (Partial)
    - [x] Analyze results (Resource Limited)
