# Separate Query LLM Support

This plan details the changes required to allow LightRAG to use a different (typically smaller and faster) LLM for queries and keyword extraction, while keeping a larger model for document processing and indexing.

## Proposed Changes

### [Component: Core]

#### [MODIFY] [base.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/base.py)
- Import `DEFAULT_QUERY_LLM_MODEL` if useful, or just handle it in `lightrag.py`.

#### [MODIFY] [lightrag.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/lightrag.py)
- Add `query_llm_model_name` and `query_llm_model_func` to the `LightRAG` dataclass.
- In `__post_init__`, initialize `query_llm_model_name` from the `QUERY_LLM_MODEL` environment variable if not already set.
- In `initialize_storages`, if `query_llm_model_name` is set, initialize `query_llm_model_func` using a similar mechanism to `llm_model_func`.
- Update `global_config` to include `query_llm_model_func`.

#### [MODIFY] [operate.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/operate.py)
- Update `kg_query`, `naive_query`, and `extract_keywords_only` to prioritize `global_config.get("query_llm_model_func")` over `global_config["llm_model_func"]` when `query_param.model_func` is None.

### [Component: Configuration]

#### [MODIFY] [.env](file:///Users/marchansen/claude_test/LightRAG/.env)
- Add `QUERY_LLM_MODEL=qwen2.5-coder:1.5b` (or similar).

## Verification Plan

### Automated Tests
- Run `benchmark_storage.py` with the new configuration.
- Add a test case that verifies different models are being called (can be verified via Langfuse traces).

### Manual Verification
- Check server logs to ensure the query model is correctly initialized.
- Verify that queries are noticeably faster with the smaller model.
