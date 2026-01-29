# Implementation Plan - ACE Core Integration (Phase 3b)

Integrate the ACE (Agentic Context Evolution) framework into the core `LightRAG` class and expose it via the FastAPI server.

## Proposed Changes

### Core System

#### [MODIFY] [lightrag.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/lightrag.py)
- Add ACE-related dataclass fields to `LightRAG`:
    - `enable_ace: bool = field(default=False)`
    - `ace_config: Optional[ACEConfig] = field(default=None)`
- Update `__post_init__` to initialize ACE components:
    - If `enable_ace` is True, it will set up `self.playbook`, `self.generator`, `self.reflector`, and `self.curator`.
- Add `ace_query` async method:
    - Parameters: `query`, `param: QueryParam`, `auto_reflect: bool = True`
    - Logic: Executes `self.generator.generate(query, param)` and optionally triggers reflection/curation.

#### [MODIFY] [lightrag_server.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/api/lightrag_server.py)
- Import `ace_query` related types if necessary.
- Add a new route handler for `POST /ace/query`.
- Ensure it uses the existing `rag` instance.

### ACE Components

#### [MODIFY] [config.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/ace/config.py)
- Update `ACEConfig` to allow its `base_dir` to be relative to the `LightRAG.working_dir`.

## Verification Plan

### Automated Tests
- **[NEW] `tests/test_ace_api.py`**:
    - Use `httpx` and `pytest-asyncio` to test the new `/ace/query` endpoint with a live or mocked server.
    - Since we have a working integration test `tests/test_ace_integration.py`, I will create a simpler version that specifically targets the API.
    - Command: `.venv/bin/python -m pytest tests/test_ace_api.py`

### Manual Verification
1. Start the LightRAG server:
   ```bash
   uv run lightrag-server
   ```
2. Call the new ACE query endpoint:
   ```bash
   curl -X POST "http://localhost:9621/ace/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the core principles of ACE?", "auto_reflect": true}'
   ```
3. Check the `rag_storage/ace/context_playbook.json` file to confirm that lessons are being added.
