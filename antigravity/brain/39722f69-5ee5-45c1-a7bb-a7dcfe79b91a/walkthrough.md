# Walkthrough: Beekeeping Test Data & Graph Construction

I have successfully tested the system's core capabilities using beekeeping examples extracted from the original LightRAG paper. This process revealed some fascinating insights into how the current system (using local LLMs) constructs knowledge graphs.

## 🐝 Beekeeping Ingestion & Retrieval

I extracted the beekeeping-related text from `docs/LightRAG-simple and fast retrieval-augmented generation.pdf` and ingested it into a fresh storage instance (`rag_storage_beekeeping`).

### Retrieval Performance

- **Hybrid Mode**: Successfully retrieved accurate definitions of a beekeeper and their practices.
- **Local Mode**: Focused on specific entity relationships found in the beekeeping text.
- **Global Mode**: Provided a higher-level summary of the role of beekeeping in agriculture.

### 🔍 Key Discovery: Hallucination by Proximity

During testing, I observed an interesting hallucination in the hybrid retrieval mode. The system suggested that "Beekeepers diagnose potential heart issues."

Upon inspecting the generated graph (`graph_chunk_entity_relation.graphml`), I found that the LLM (`qwen2.5-coder:1.5b`) created a direct relationship between **Beekeeper** and **Heart Disease**.

```xml
<edge source="Beekeeper" target="Heart Disease">
  <data key="d8">Beekeepers diagnose potential heart issues, contributing to their overall health and productivity in agriculture.</data>
</edge>
```

**Why did this happen?**
The source text contained an example about Cardiologists diagnosing heart disease immediately following a description of beekeeping practices. The small local LLM incorrectly merged these contexts into a single relationship.

> [!IMPORTANT]
> This discovery perfectly validates the need for **ACE Phase 3**, where the **Reflector** component will be designed to identify such logical errors in the graph and the **Curator** will apply repairs.

## 📊 Graph Construction Comparison

As requested, I've analyzed how LightRAG's construction compares to standard Neo4j/MemGraph approaches.

| Feature | LightRAG | Standard Neo4j/MemGraph |
| :--- | :--- | :--- |
| **Logic** | RAG-Optimized (Rich descriptions on edges/nodes) | Schema-Optimized (Atomic properties) |
| **Deduplication** | LLM-based profiling during ingestion | Often requires external entity resolution |
| **Complexity** | Higher density of textual context in the graph | Higher structure density, lower text density |

### Verification of WebUI Visualization

I've verified that the existing `GraphViewer.tsx` (using Sigma.js) is capable of rendering these complex relationships. You can view the newly generated beekeeping graph in the "Knowledge Graph" tab of the WebUI.

## Next Steps

- [ ] Implement the **Reflector** logic to catch the "Beekeeper -> Heart Disease" error.
- [ ] Implement the **Curator** logic to prune/repair such edges.
- [ ] Add reranking and ACE controls to the WebUI.
