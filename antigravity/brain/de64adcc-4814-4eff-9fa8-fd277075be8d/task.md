# Task: ACE Framework Integration (Phase 3)

## Preparation
- [ ] Create `lightrag/ace` directory and `__init__.py`

## Implementation (Minimal Prototype)
- [ ] Implement `lightrag/ace/config.py`
- [x] **ACE Framework Integration (Phase 3)**
    - [x] Initial Directory Structure (`lightrag/ace/`)
    - [x] Core Configuration (`config.py`)
    - [x] Persistent Playbook (`playbook.py`)
    - [x] Generator (Query Wrapper) (`generator.py`)
    - [x] Reflector (Insight Extractor) (`reflector.py`)
    - [x] Curator (Playbook Updater) (`curator.py`)
    - [x] Unit Tests (`tests/test_ace_components.py`)
    - [x] Integration Test (Live LLM Loop) (`tests/test_ace_integration.py`)
    - [x] Implement `/ace/query` API endpoint [lightrag/api/routers/query_routes.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/api/routers/query_routes.py)
    - [x] Implement `ACEQueryRequest` and `ACEQueryResponse` models
    - [x] Add `--enable-ace` flag to API configuration [lightrag/api/config.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/api/config.py)
    - [x] Verify API integration with `tests/test_ace_api.py` [tests/test_ace_api.py](file:///Users/marchansen/claude_test/LightRAG/tests/test_ace_api.py)
- [x] Manual verification of end-to-end flow
- [ ] Verify the full cycle: Query -> Generate -> Reflect -> Curate
