# Walkthrough: Evaluation & Testing Standardization

We have successfully standardized the evaluation and testing framework for LightRAG. This walkthrough demonstrates the new tiered testing strategy and the integrated observability.

## 🏆 Summary of Accomplishments

1. **Tiered Testing Strategy**: Implemented `light` and `heavy` markers in `conftest.py` to separate quick verification from long-running benchmarks.
2. **RAGAS Integration**: Created `tests/test_rag_quality.py` as a pytest wrapper for the RAGAS evaluation script.
3. **Observability**: Integrated Langfuse for full-chain tracing and metric mapping.
4. **Comprehensive Documentation**: Created detailed guides for Observability, Evaluation, and the ACE Framework.

## 🧪 Verification: The Light Path

The "Light Path" verifies the entire evaluation pipeline (indexing, retrieval, RAGAS scoring, results generation) with a single test case.

```bash
uv run pytest tests/test_rag_quality.py --run-light --run-integration -s -v
```

### ✅ Results

The pipeline successfully indexed sample documents and generated a RAGAS score using local LLMs.

**Output Fragment:**

```text
INFO: 🚀 Starting RAGAS Evaluation of LightRAG System
Eval-01:  100%|██████████| 4/4 [17:16<00:00, 259.24s/it]
INFO: Average RAGAS Score:       0.6966
INFO: Results Dir:    /Users/marchansen/antigravity_lightrag/LightRAG/lightrag/evaluation/results
PASSED
```

## 🔭 Observability in Action

With `LANGFUSE_ENABLE_TRACE=true`, every evaluation trace is streamed to Langfuse.

> [!NOTE]
> Detailed traces including LLM prompts, token usage, and latency are available in the local Langfuse dashboard at <http://localhost:3000>.

## 📖 New Documentation

The following guides are now available in the `docs/` directory:

- [**OBSERVABILITY.md**](../../../../antigravity_lightrag/LightRAG/docs/OBSERVABILITY.md): Langfuse setup and usage.
- [**EVALUATION.md**](../../../../antigravity_lightrag/LightRAG/docs/EVALUATION.md): RAGAS metrics and benchmarking.
- [**ACE_FRAMEWORK.md**](../../../../antigravity_lightrag/LightRAG/docs/ACE_FRAMEWORK.md): Theoretical and operational overview of ACE.

## 📝 Markdown Standardization & SOP Update

To ensure consistent document quality and resolve rendering issues (e.g., "literal text" links), we have integrated a markdown linter into the project's Standard Mission Protocol (SMP).

### 🛠️ Key Changes

- **Rendering Fix**: Standardized `GLOBAL_INDEX.md` to use relative paths for local files, ensuring compatibility with all markdown renderers.
- **Linting Integration**: Installed `markdownlint-cli` and enabled it in the **Pre-Flight Check (PFC)** and **Return To Base (RTB)** procedures in `GEMINI.md`.
- **System Configuration**: Created `.markdownlint.json` to manage stylistic rules (like ignoring line lengths for long links) across the system.

### ✅ Verification

All documentation files now pass `markdownlint` verification, ensuring zero formatting errors before session closure.

```bash
# Example verification command
markdownlint GLOBAL_INDEX.md
# Output: Success (No errors)
```

## 📊 Roadmap Update

The project roadmap has been updated to reflect the new standardized state.

```markdown
- ✓ **Evaluation & Testing Standardization** (2026-01-26): Implemented tiered testing, integrated Langfuse, and created documentation.
- ✓ **Markdown Standards & SOP Integration** (2026-01-27): Integrated `markdownlint` into SMP and fixed index rendering.
```
