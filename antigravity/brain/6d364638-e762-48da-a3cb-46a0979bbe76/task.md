# Tasks

- [x] Fix Dark Mode Flash `lightrag-nbi`
- [x] Setting up Evaluation Framework (RAGAS + Langfuse) `lightrag-j09`
- [x] Standardizing Evaluation & Observability Documentation and Testing `lightrag-doc-test`
  - [x] Create `docs/OBSERVABILITY.md`
  - [x] Create `docs/EVALUATION.md`
  - [x] Create `docs/ACE_FRAMEWORK.md`
  - [x] Update `ROADMAP.md`
  - [x] Modify `tests/conftest.py` for tiered testing
  - [x] Create `tests/test_rag_quality.py` wrapper
  - [x] Verify "Light Path" (`pytest tests/test_rag_quality.py --run-light`)
  - [x] Update `tests/test_benchmarks.py` markers
- [x] Verify and standardize Global Index link integrity `lightrag-links`
  - [x] Standardize `GLOBAL_INDEX.md` with relative paths (GFM compatible)
- [x] Fix Markdown rendering and integrate linting into SOP `lightrag-md-sop`
  - [x] Resolve Rendering/broken links in `GLOBAL_INDEX.md`
  - [x] Install and configure `markdownlint-cli`
  - [x] Add markdown linting to `GEMINI.md` / SMP
