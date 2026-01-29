# Fix Ragas Metrics Type Compatibility

## Goal Description
The standard `ragas.evaluate()` function requires metrics to inherit from `ragas.metrics.base.Metric`. In Ragas 0.4.3, the "Collections" metrics (which are encouraged via deprecation warnings) inherit from `SimpleBaseMetric`, which is NOT a subclass of `Metric`. This causes a `TypeError` when using `evaluate()`.
To resolve this, we must switch back to using the "Legacy" metrics (available via `ragas.metrics`) and the "Legacy" wrappers (`LangchainLLMWrapper`, `LangchainEmbeddingsWrapper`), which are compatible with the `Metric` class hierarchy expected by `evaluate()`.

## User Review Required
None. This is a fix for the evaluation script.

## Proposed Changes
### LightRAG
#### [MODIFY] [eval_rag_quality.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/evaluation/eval_rag_quality.py)
- Remove imports from `ragas.metrics.collections`. Force import from `ragas.metrics`.
- Use `LangchainLLMWrapper` for LLM (and `ChatOpenAI`).
- Use `LangchainEmbeddingsWrapper` for Embeddings (and `OpenAIEmbeddings`/`OllamaEmbeddings`).
- Suppress deprecation warnings related to these legacy imports.
- Ensure `llm` and `embeddings` are passed to the metric constructors.

## Verification Plan
### Automated Tests
Run the evaluation script.
```bash
cd /Users/marchansen/claude_test/LightRAG
# Ensure we use the correct python environment
python lightrag/evaluation/eval_rag_quality.py
```
If the script runs producing results without type errors, the fix is verified.
