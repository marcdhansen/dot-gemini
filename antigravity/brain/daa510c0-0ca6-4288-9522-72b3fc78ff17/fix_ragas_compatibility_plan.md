# Fix Ragas LLM Compatibility

## Goal Description
The Ragas evaluation failed with `Collections metrics only support modern InstructorLLM`. This is because Ragas 0.4.x metrics require `InstructorLLM` (or compatible), while the current code uses the deprecated `LangchainLLMWrapper`.
This plan updates `eval_rag_quality.py` to use `llm_factory` with an OpenAI-compatible client (pointing to Ollama) to create a compatible LLM instance. It also wraps the LangChain embeddings with `LangchainEmbeddingsWrapper` to ensure full compatibility.

## User Review Required
None. This is a fix for the evaluation script.

## Proposed Changes
### LightRAG
#### [MODIFY] [eval_rag_quality.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/evaluation/eval_rag_quality.py)
- Import `OpenAI` from `openai`.
- Import `llm_factory` from `ragas.llms`.
- Import `LangchainEmbeddingsWrapper` from `ragas.embeddings`.
- Replace `LangchainLLMWrapper` usage with:
  ```python
  from openai import OpenAI
  client = OpenAI(base_url=..., api_key=...)
  self.eval_llm = llm_factory(model=..., client=client)
  ```
- Wrap `OllamaEmbeddings`/`OpenAIEmbeddings` with `LangchainEmbeddingsWrapper`:
  ```python
  base_embeddings = OllamaEmbeddings(...)
  self.eval_embeddings = LangchainEmbeddingsWrapper(base_embeddings)
  ```
- Ensure `self.eval_llm` and `self.eval_embeddings` are passed to metrics (already done in previous step).

## Verification Plan
### Automated Tests
Run the evaluation script again.
```bash
cd /Users/marchansen/claude_test/LightRAG
# Ensure we use the correct python environment
python lightrag/evaluation/eval_rag_quality.py
```
If the script runs without the compatibility error and produces results, the fix is verified.
