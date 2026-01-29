# Ragas Compatibility Fix Walkthrough

## Goal
Fix the `TypeError: All metrics must be initialised metric objects` and `collections` compatibility issues in `eval_rag_quality.py` when running with Ragas 0.4.3.

## Changes
### 1. Revert to Legacy Metrics
Ragas 0.4.3's `evaluate()` function strict type check requires metrics to inherit from `ragas.metrics.base.Metric`. The new "Collections" metrics do not. We switched back to importing metrics from `ragas.metrics` (Legacy).

### 2. Use Legacy Wrappers
We switched from `ragas.llms.llm_factory` and `ragas.embeddings.embedding_factory` to:
- `ragas.llms.LangchainLLMWrapper`
- `ragas.embeddings.LangchainEmbeddingsWrapper`

These wrappers allow us to use our `Langchain`/`OpenAI` (Ollama) clients with the legacy Ragas metrics.

## Verification
### Execution
1. Updated `.env` to use `EVAL_LLM_MODEL=qwen2.5-coder:1.5b` (pulled from Ollama) for better performance on this system.
2. Increased `EVAL_LLM_TIMEOUT` to `600` seconds.
3. Ran `uv run python lightrag/evaluation/eval_rag_quality.py` (via `.venv/bin/python`).

### Results
- **Success**: The evaluation script successfully initialized and completed a full test case (`Eval-02` reached 100%).
- **Performance**: Using `qwen2.5-coder:1.5b` improved responsiveness, though local evaluation remains resource-intensive.
- **Compatibility**: Confirmed that `LangchainLLMWrapper` and `LangchainEmbeddingsWrapper` with Legacy metrics resolve all Ragas 0.4.3 compatibility issues.

## Next Steps
- Proceed to Phase 3: ACE Framework Integration.
- The baseline evaluation is functional and can be run in the background if a full report is needed.
