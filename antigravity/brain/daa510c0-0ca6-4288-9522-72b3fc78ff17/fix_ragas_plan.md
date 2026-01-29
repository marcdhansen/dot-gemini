# Fix Ragas Metric Initialization Error

## Goal Description
The recent Ragas evaluation failed with `TypeError: Faithfulness.__init__() missing 1 required positional argument: 'llm'`. This indicates that the installed version of `ragas` requires the `llm` argument to be passed explicitly during metric instantiation, or at least for `Faithfulness`.
This plan updates `lightrag/evaluation/eval_rag_quality.py` to correctly instantiate Ragas metrics by passing the configured `llm` and `embeddings` where appropriate.

## User Review Required
None. This is a bug fix for the evaluation script.

## Proposed Changes
### LightRAG
#### [MODIFY] [eval_rag_quality.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/evaluation/eval_rag_quality.py)
- Update `evaluate_single_case` to instantiate metrics with `llm` argument.
- Specifically, change `Faithfulness()` to `Faithfulness(llm=self.eval_llm)`.
- Also update `AnswerRelevancy(llm=self.eval_llm, embeddings=self.eval_embeddings)`.
- Update `ContextRecall(llm=self.eval_llm)` and `ContextPrecision(llm=self.eval_llm)` if applicable, or check if they need it. (Safest to pass it if they accept it, but `ragas` metrics usually take `llm` in `init`).

## Verification Plan
### Automated Tests
Run the evaluation script with the sample dataset.
```bash
cd /Users/marchansen/claude_test/LightRAG
# Ensure we use the correct python environment
python lightrag/evaluation/eval_rag_quality.py
```
If the script runs without the `TypeError` and produces results (even if 0), the fix is verified.
