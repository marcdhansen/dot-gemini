# Fix Evaluation 404 Error (Native Ollama Embeddings)

## Problem
The evaluation script `eval_rag_quality.py` is hardcoded to use `OpenAIEmbeddings`. When configured with Ollama at `http://localhost:11434`, it attempts to hit `http://localhost:11434/embeddings`, which does not exist, causing a 404. Ollama's OpenAI-compatible endpoint is at `/v1/embeddings`, while its native endpoint is at `/api/embeddings`.

## Proposed Solution
Update `eval_rag_quality.py` to support multiple embedding bindings, specifically adding support for the native `ollama` binding using `OllamaEmbeddings` from `langchain_community`.

## Proposed Changes

### [MODIFY] [eval_rag_quality.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/evaluation/eval_rag_quality.py)
- Import `OllamaEmbeddings` from `langchain_community.embeddings`.
- Update `RAGEvaluator.__init__` to check `os.getenv("EVAL_EMBEDDING_BINDING")`.
- If binding is `ollama`, initialize `OllamaEmbeddings` using `EVAL_EMBEDDING_BINDING_HOST`.
- Otherwise, default to `OpenAIEmbeddings` (ensuring compatibility with existing OpenAI configs).

## Verification Plan
1. Run `eval_rag_quality.py` with current `.env` (which has `EVAL_EMBEDDING_BINDING=ollama`).
2. Confirm Stage 2 scoring starts without 404 errors.
