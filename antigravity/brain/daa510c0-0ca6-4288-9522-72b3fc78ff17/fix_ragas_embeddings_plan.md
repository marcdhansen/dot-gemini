# Fix Ragas Embeddings Compatibility

## Goal Description
The previous attempt to fix Ragas compatibility failed because `LangchainEmbeddingsWrapper` is also deprecated and incompatible with `Collections` metrics. The error message explicitly recommends using `embedding_factory`.
This plan updates `eval_rag_quality.py` to use `embedding_factory` for initializing embeddings, passing the same OpenAI-compatible client (configured for Ollama) as used for the LLM.

## User Review Required
None. This is a continued fix for the evaluation script.

## Proposed Changes
### LightRAG
#### [MODIFY] [eval_rag_quality.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/evaluation/eval_rag_quality.py)
- Import `embedding_factory` from `ragas.embeddings`.
- Remove `LangchainEmbeddingsWrapper` usage.
- Initialize embeddings using `embedding_factory` with the OpenAI client.
  ```python
  from ragas.embeddings import embedding_factory
  # ...
  self.eval_embeddings = embedding_factory(
      provider="openai",
      model=eval_embedding_model,
      client=client
  )
  ```
- Reuse the `client` created for `llm_factory` if possible, or create a new one if endpoints differ. (The current script handles different endpoints, so we might need separate clients if LLM and Embeddings point to different URLs, but in the default local Ollama case, they are likely the same or similar. The script already has logic for this).

## Verification Plan
### Automated Tests
Run the evaluation script again.
```bash
cd /Users/marchansen/claude_test/LightRAG
# Ensure we use the correct python environment
python lightrag/evaluation/eval_rag_quality.py
```
If the script runs without the compatibility error and produces results, the fix is verified.
