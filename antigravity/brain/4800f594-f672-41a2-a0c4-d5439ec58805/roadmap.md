# LightRAG Project Roadmap

## 1. Immediate Maintenance & Fixes
- [ ] **Fix Ragas Deprecation Warning**: Update imports in `eval_rag_quality.py` to use `ragas.metrics.collections`.
- [x] **Fix Reranking Warning** <!-- id: LightRAG-o5v -->: Configure a local Ollama reranking model to suppress "rerank enabled but no model" warnings.

## 2. Documentation & Research
- [ ] **Ragas Summary**: Summarize what RAGAS does (faithfulness, relevance, context quality assessment) and add to the Evaluations documentation.
- [ ] **Langfuse Investigation**: Summarize Langfuse capabilities (traces, costs, evals) and add to the Observability documentation.
- [ ] **ACE Integration**: Add link to [ACE github repo](https://github.com/ace-agent/ace) in documentation. Verify if the server can pass tests from the ACE repo.
- [ ] **Evolution Research**: Add link to [MemEvolve github repo](https://github.com/bingreeky/MemEvolve) in the self-evolution section.

## 3. Strategic Enhancements: Agentic RAG
*Goal: Define the "Brain" of the RAG system*
- [ ] **Agent Capabilities**:
    - Select retrieval method(s) dynamically.
    - Select LLM model based on task complexity.
    - Determine optimal chunking strategy (size, overlap, method).
- [ ] **Prompt & Response Tracking**: Research solutions (Langfuse, Phoenix, Weave, or custom logging).
- [ ] **Memory Integration**: Investigate [MemGPT](https://memgpt.ai/) (or open source Letta) for persistent agent memory.

## 4. Exploration & Experiments
- [ ] **RAG Modes Benchmarking**:
    - Naive vs. Local vs. Global vs. Hybrid vs. Mix (Graph + Vector).
- [ ] **Advanced Graph Features**:
    - Support for "Cold" Graph (Neo4j persistence).
    - Support for Temporal Graphs (handling time-series or sequential data).
- [ ] **Self-Healing**: Investigate mechanisms similar to Greptile.
- [ ] **Testing Frameworks**: Develop framework for testing strategies like contextual chunking or late chunking.
- [ ] **External Inspirations**: Review [n8n harness video](https://youtu.be/RQq3aMV7a5g?si=qfsbiuSGN33DVMrZ) to understand their approach.
