# Standardizing Evaluation, Observability, and Testing Frameworks

This plan outlines the steps to document the key frameworks used in LightRAG (Langfuse, RAGAS, ACE) and integrate RAGAS evaluations into the standard pytest framework with a tiered testing strategy (Light vs. Heavy).

## Proposed Changes

### 📝 Documentation Layer

#### [NEW] [OBSERVABILITY.md](../../../../antigravity_lightrag/LightRAG/docs/OBSERVABILITY.md)

Document the benefits of Langfuse, setup instructions (Docker), and how it integrates with LightRAG for tracing, latency tracking, and cost analysis.

#### [NEW] [EVALUATION.md](../../../../antigravity_lightrag/LightRAG/docs/EVALUATION.md)

Detailed discussion on RAGAS (Faithfulness, Relevance, Recall, Precision), why it's used, how to interpret scores, and how to run evaluations using local Ollama models.

#### [NEW] [ACE_FRAMEWORK.md](../../../../antigravity_lightrag/LightRAG/docs/ACE_FRAMEWORK.md)

Document the **Agentic Context Evolution (ACE)** framework, covering components like Curator, Reflector, Generator, and Playbooks.

#### [MODIFY] [ROADMAP.md](../../../../antigravity_lightrag/LightRAG/.agent/rules/ROADMAP.md)

Update the roadmap to include finalized observability and evaluation milestones.

---

### 🧪 Testing Layer

#### [MODIFY] [conftest.py](../../../../antigravity_lightrag/LightRAG/tests/conftest.py)

- Register `light` and `heavy` markers.
- Update `pytest_collection_modifyitems` to support selecting `light` or `heavy` paths via CLI flags or markers.
- Ensure `light` tests run by default or via `pytest -m light`.
- Ensure `heavy` tests (including academic benchmarks and full RAGAS runs) are skipped unless explicitly requested via `pytest -m heavy`.

#### [NEW] [test_rag_quality.py](../../../../antigravity_lightrag/LightRAG/tests/test_rag_quality.py)

Create a pytest wrapper for the existing `eval_rag_quality.py` script.

- **Light Path**: Run a single test case (e.g., from `sample_dataset.json`) to verify the integration is working. Marked with `@pytest.mark.light`.
- **Heavy Path**: Run the full evaluation suite (e.g., `bcbc_testset.json`). Marked with `@pytest.mark.heavy` and `@pytest.mark.benchmark`.

#### [MODIFY] [test_benchmarks.py](../../../../antigravity_lightrag/LightRAG/tests/test_benchmarks.py)

Ensure all existing academic-style benchmarks are marked as `heavy`.

---

## Verification Plan

### Automated Tests

1. **Light Path**: Run `pytest -m light` and verify it completes quickly (under 2 minutes) and confirms RAGAS integration.
2. **Heavy Path (Dry Run)**: Run `pytest -m heavy` with a small limit or just verify the collection includes the full suite.
3. **Marker Integrity**: Verify `pytest --markers` shows the new `light` and `heavy` markers.

### Manual Verification

1. Verify all new MD files are correctly cross-linked and readable.
2. Check that Langfuse traces appear during the `light` path execution.
