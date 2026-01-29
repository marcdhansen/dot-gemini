# Task: Fix LightRAG Timeout for PDF Upload

## Status
- [x] Investigate timeout error
    - [x] Locate relevant logs and error trace <!-- id: 0 -->
    - [x] Trace timeout configuration flow in code <!-- id: 1 -->
    - [x] Initial analysis of `ollama.py` and `lightrag_server.py` <!-- id: 2 -->
- [x] Create Reproduction Test <!-- id: 3 -->
    - [x] Create reproduction test case (`tests/test_ollama_timeout.py`)
    - [x] Verify test fails/times out with short timeout configuration <!-- id: 5 -->
- [x] Fix the issue
    - [x] Increase default timeout configuration
    - [x] Update documentation/examples
- [x] Fix Timeout Issue <!-- id: 6 -->
    - [x] Increase `DEFAULT_LLM_TIMEOUT` in `constants.py` <!-- id: 7 -->
    - [x] Update `env.example` to reflect new default <!-- id: 8 -->
- [x] Verify the fix
    - [x] Run reproduction test
    - [x] Verify with actual file upload
- [x] Verification <!-- id: 9 -->
    - [x] Run `tests/test_ollama_timeout.py` to ensure timeout logic still holds <!-- id: 10 -->
    - [x] (Optional) Manual verification or further testing instructions <!-- id: 11 -->
