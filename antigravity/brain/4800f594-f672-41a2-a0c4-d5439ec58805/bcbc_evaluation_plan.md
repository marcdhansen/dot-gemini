# BCBC Evaluation Plan

## Goal
Perform a comprehensive RAGAS evaluation on the `final_report_BCBC.pdf` (British Columbia Building Code) dataset to establish a quality baseline for the LightRAG system.

## ⚠️ Challenges & Requirements
- **Missing Dataset**: The "BCBC-specific test dataset" mentioned in previous plans could not be located. We must generate a new one.
- **Model Selection**: We will use `qwen2.5-coder:1.5b` for generation (or `llama3.2:3b` if enabled) and `qwen2.5-coder:0.5b` as the Judge (optimized for speed).

## Proposed Workflow

### 1. Generate Ground Truth Dataset (`bcbc_testset.json`)
We need a set of (Question, Ground_Truth, Context) triplets.
- **Action**: Create a script `start_bcbc_eval.py` that:
    1.  Reads the text content of `final_report_BCBC.pdf` (already ingested).
    2.  Uses an LLM to generate 20-50 high-quality Questions and Answers based on the text.
    3.  Saves them in Ragas-compatible JSON format.

### 2. Configure Evaluation
- **Script**: `lightrag/evaluation/eval_rag_quality.py`
- **Config**:
    - `EVAL_LLM_MODEL`: `qwen2.5-coder:1.5b` (as configured in `.env`)
    - `EVAL_EMBEDDING_MODEL`: `nomic-embed-text:v1.5`
    - `RAGAS_METRICS`: Faithfulness, Answer Relevance, Context Precision, Context Recall.

### 3. Execution
- Run `python lightrag/evaluation/eval_rag_quality.py --dataset bcbc_testset.json`
- Monitor for timeouts (PDF processing is heavy).

## Verification
- **Success Criteria**:
    - Testset file `bcbc_testset.json` exists and contains valid JSON.
    - Evaluation script finishes without `TimeoutError`.
    - Ragas scores are generated (Reference: >0.7 is good, <0.4 needs improvement).
