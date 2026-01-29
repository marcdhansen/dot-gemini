# Fix LightRAG Timeout Error for Large PDF Uploads

The uploading of `final_report BCBC.pdf` fails with an `httpx.ReadTimeout` because the default LLM timeout (180s) is exceeded during the entity extraction phase with Ollama. This plan proposes determining the timeout enforcement mechanism via a new test and then increasing the default timeout to accommodate larger documents.

## User Review Required
> [!IMPORTANT]
> I will be increasing the `DEFAULT_LLM_TIMEOUT` from 180s to 600s (10 minutes) to handle larger documents. This change affects all users who haven't explicitly set `LLM_TIMEOUT` in their environment.

## Proposed Changes

### LightRAG Core
#### [MODIFY] [constants.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/constants.py)
- Increase `DEFAULT_LLM_TIMEOUT` constant from `180` to `600`.

#### [MODIFY] [env.example](file:///Users/marchansen/claude_test/LightRAG/env.example)
- Update code comments and examples to reflect the new default or suggest a higher value.

### Tests
#### [NEW] [tests/test_ollama_timeout.py](file:///Users/marchansen/claude_test/LightRAG/tests/test_ollama_timeout.py)
- A new test file using `pytest` and `unittest.mock`.
- **Test Case 1 (Reproduction)**: configure `LightRAG` with a very short timeout (e.g., 0.1s) and mock the Ollama client to sleep for longer. Assert that `APITimeoutError` (or the underlying `httpx.ReadTimeout` wrapped) is raised.
- **Test Case 2 (Verification)**: configure `LightRAG` with a longer timeout and mock the Ollama client to sleep for a shorter duration. Assert success.

## Verification Plan

### Automated Tests
- Run the newly created test:
  ```bash
  pytest tests/test_ollama_timeout.py
  ```
