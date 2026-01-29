# Performance Investigation: Query Answering Slowdown (LightRAG-bbt)

## Problem Summary

RAGAS evaluation fails because each query takes >600 seconds with local LLMs (granite4:3b, llama3.2:3b), causing HTTP timeouts.

## Root Cause Analysis

**Timing Breakdown per Query:**
| Stage | Time | Notes |
|-------|------|-------|
| Keyword extraction | ~15-20s | LLM call, acceptable |
| Retrieval (NetworkX) | <1s | Fast, but graph size is small |
| **Answer generation** | **~200s** | **Current Baseline ( llama3.2:3b, CoT=False, TOP_K=5)** |

**Why is answer generation slow?**

1. **Large Context Size:** The `rag_response` prompt includes 13-30 entities, 10-12 relations, and 3 chunks, totaling ~4,000-8,000 tokens.
2. **Hardcoded CoT:** `kg_query` in `operate.py` hardcodes `enable_cot=True`. Local 3B models generating long "thinking" blocks take significant time.

Local 3B models like `granite4:3b` process tokens at ~10-30 tokens/second. Generating a multi-paragraph response (~500+ tokens) from this context takes 300-600+ seconds.

**Comparison with entity extraction:**
- Entity extraction uses smaller chunks (~1200 tokens) with simpler output format
- Answer generation requires reasoning over larger context with complex output

## Proposed Solutions

### Option 1: Reduce Context Size (Quick Win)

Reduce the number of entities, relations, and chunks sent to LLM:

**Files to modify:**
- [MODIFY] [.env](file:///Users/marchansen/claude_test/LightRAG/.env)

**Changes:**
```env
# Add/modify these values to reduce context
QUERY_TOP_K=5           # Default: 10-40
QUERY_CHUNK_TOP_K=2     # Default: 20  
MAX_ENTITY_TOKENS=500   # Default: 4000
MAX_RELATION_TOKENS=500 # Default: 4000
```

**Pros:** No code changes, quick to test
**Cons:** May reduce answer quality

---

### Option 2: Enable LLM Response Caching

Cache LLM responses to avoid repeated LLM calls for same queries.

**Files to modify:**
- [MODIFY] [.env](file:///Users/marchansen/claude_test/LightRAG/.env)

**Changes:**
```env
LLM_CACHE_ENABLED=true
```

**Pros:** Subsequent queries are instant
**Cons:** Only helps for repeated queries

---

### Option 3: Use Cloud API for RAGAS Evaluation

Keep local LLM for data processing, use cloud API (OpenAI) only for RAGAS evaluation.

**Files to modify:**
- [MODIFY] [.env](file:///Users/marchansen/claude_test/LightRAG/.env)

**Changes:**
```env
# RAGAS evaluation uses OpenAI while server uses local LLM
EVAL_LLM_MODEL=gpt-4o-mini
EVAL_LLM_BINDING_API_KEY=<your-openai-key>
EVAL_LLM_BINDING_HOST=   # Leave empty for OpenAI default
```

**Pros:** RAGAS runs in seconds, high quality evaluation
**Cons:** Requires OpenAI API key and costs money

---

### Option 4: Disable Chain of Thought (CoT)

Disable reasoning tokens to reduce total tokens generated.

**Files to modify:**
- [MODIFY] [operate.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/operate.py)

**Changes:**
Change `enable_cot=True` to `False` in `kg_query`.

**Pros:** Significantly reduces total generation time
**Cons:** May reduce reasoning quality

---

### Option 5: Separate Query LLM Model

Allow using a smaller/faster LLM model specifically for query answering (e.g., `qwen2.5:0.5b`) while maintaining a higher-quality model for extraction.

**Files to modify:**
- [MODIFY] [.env](file:///Users/marchansen/claude_test/LightRAG/.env)
- [MODIFY] [lightrag.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/lightrag.py)

**Changes:**
1. Introduce `QUERY_LLM_MODEL` in `.env`.
2. Update `LightRAG` initialization to support separate `query_llm_model_func`.

**Pros:** Optimized speed for query while keeping extraction quality.
**Cons:** Requires additional code modification to support separate models.

---
NetworkX Baseline: **215.72s** (llama3.2:3b on CPU, CoT disabled).
- Status: Memgraph- NetworkX Query Baseline (rag_storage): **215.72 seconds**
- Memgraph Query Performance (rag_storage): **72.47 seconds** (~66% faster)
- Ollama CPU Extraction time (BCBC report): **~5 hours** (3 chunks)

### Option 6: Switch Graph Storage to Memgraph

Switch from default `NetworkXStorage` (Python in-memory) to `MemgraphStorage` (high-performance graph database).

**1. Start Memgraph via Docker:**
```bash
docker compose -f docker-compose.memgraph.yml up -d
```
*   **Bolt URI:** `bolt://localhost:7687`
*   **Lab UI:** `http://localhost:3001`

**2. Update [.env](file:///Users/marchansen/claude_test/LightRAG/.env):**
```env
LIGHTRAG_GRAPH_STORAGE=MemgraphStorage
MEMGRAPH_URI=bolt://localhost:7687
```

**Pros:** Optimized for graph traversals, persistent storage, visual inspection via Memgraph Lab.
**Cons:** Requires Docker. Initial index creation may take a few seconds.

---

## Recommended Approach

1. **Immediate:** Reduce context size (Option 1) AND Disable CoT (Option 4).
2. **Efficiency:** Use a separate, smaller LLM for queries (Option 5) to boost speed.
3. **If still slow:** Use Cloud API for RAGAS evaluation (Option 3).
4. **Architecture:** Experiment with Memgraph (Option 6) for faster retrieval if graph traversal becomes a bottleneck.

## Verification Plan

### Test Reduced Context Size
```bash
# 1. Update .env with reduced context settings
# 2. Restart server
cd /Users/marchansen/claude_test/LightRAG && pkill -f lightrag-server; uv run lightrag-server &

# 3. Test a single query with timing
time curl -s -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the authors of the BCBC report?", "mode": "mix"}' | head -100

# Success: Query completes in <120 seconds
```

### Test RAGAS with Single Question (after fix)
```bash
cd /Users/marchansen/claude_test/LightRAG
python -c "
import asyncio
from lightrag.evaluation.eval_rag_quality import RAGEvaluator
evaluator = RAGEvaluator(test_dataset_path='lightrag/evaluation/bcbc_test_dataset.json')
# Test just first question
asyncio.run(evaluator.run())
"
# Success: At least 1 question completes without timeout
```
