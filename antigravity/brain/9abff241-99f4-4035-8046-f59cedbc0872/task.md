# LightRAG-bbt: Query Performance Fix

## Status: ✅ Performance fixed (Option 1 & 4 applied), testing RAGAS

| Metric | Before | After | Notes |
|--------|--------|-------|-------|
| Query time | >600s timeout | ~110s | With context reduced to 5 entities |
| CoT | Enabled (True) | Disabled (False) | Speeds up response generation |

## Tasks

- [x] Identify performance bottleneck in `kg_query` (CoT + large context)
- [x] Apply Option 1: Reduce context size via `.env` (`TOP_K=5`, etc.)
- [x] Apply Option 4: Disable hardcoded `enable_cot=True` in `operate.py`
- [x] Install RAGAS dependencies (`ragas`, `datasets`)
- [x] Increase RAGAS LLM timeouts and retries in `.env`
- [x] Run RAGAS evaluation baseline
- [x] Clear current storage for clean start
- [x] Re-index document into Memgraph (3/3 chunks done)
- [x] Verify node count in Memgraph after indexing completes (24 nodes found)
    - [x] Configure `.env` for Memgraph
    - [x] Capture NetworkX baseline: **215.72s**
- [x] Benchmark Memgraph Performance: **72.47s** (NetworkX: 215.72s)
- [x] Document performance comparison and finalize report
- [x] Implement Option 5: Separate Query LLM model support
    - [x] Add `QUERY_LLM_MODEL` to `.env`
    - [x] Modify `LightRAG` and `aquery_llm` to use separate query model if provided
- [x] Long-Term Planning (LTP): Update project roadmap and TODO
- [ ] Verify system with `dickens_short.txt` (fast test) (LightRAG-0y6)

## Root Cause Analysis
1. **Large Context:** 30+ entities and 10+ relations created ~8,000 token prompts, overwhelming local 3B CPU inference.
2. **Hardcoded CoT:** `operate.py` forced local models to think extensively, adding minutes of generation time.

## Recommended Next Steps
1. Monitor RAGAS evaluation progress.
2. Consider even smaller models (e.g. 0.5b) specifically for simple keyword extraction.
