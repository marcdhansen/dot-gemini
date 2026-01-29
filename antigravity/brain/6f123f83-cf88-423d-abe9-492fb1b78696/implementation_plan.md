# Plan: Detailed Subsystem Documentation

The goal of this task is to provide comprehensive, technical documentation for the major subsystems within LightRAG. Each document will include architectural diagrams (Mermaid), implementation details, and interaction flows.

## Proposed Changes

### [Documentation]

#### [NEW] [ACE.md](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/subsystems/ACE.md)

Detailed breakdown of the Agentic Context Evolution framework, covering:

- **Curator**: Context optimization logic.
- **Reflector**: Feedback loop and insight generation.
- **Generator**: Enhanced response generation using evolving context.
- **Playbooks**: Persistence and application of lessons learned.
- *Diagram*: ACE Loop and component interactions.

#### [NEW] [OBSERVABILITY.md](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/subsystems/OBSERVABILITY.md)

Focus on Langfuse and tracing:

- Integration points in `openai.py`.
- Tracing of LLM calls, cache hits, and pipeline stages.
- Integration with RAGAS for evaluation metrics.
- *Diagram*: Trace flow from API request to evaluation.

#### [NEW] [GRAPH_STORAGE.md](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/subsystems/GRAPH_STORAGE.md)

Deep dive into MemGraph (and Neo4j compatible) storage:

- Schema design (`entity_id` based).
- Workspace partitioning logic.
- Integrated vector search (Memgraph vector index).
- Transactional integrity and retry mechanisms.
- *Diagram*: Node-Edge schema and vector index mapping.

#### [NEW] [UI_FEATURES.md](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/subsystems/UI_FEATURES.md)

Documentation of high-impact UI features:

- **Semantic Highlighting**: Backend Zilliz model integration and frontend display.
- **Graph Visualization**: Interactive canvas details and data binding.
- *Diagram*: Frontend-Backend data flow for highlighting and graph rendering.

#### [NEW] [EXTRACTION.md](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/subsystems/EXTRACTION.md)

Detailed extraction pipeline:

- Token-based chunking strategy.
- Standard vs. YAML-based extraction logic.
- Merge-reduce summarization for entities and relations.
- *Diagram*: Document processing pipeline from raw text to knowledge graph.

### [Integration]

#### [MODIFY] [ARCHITECTURE.md](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/ARCHITECTURE.md)

Update the main architecture doc to serve as a hub, linking to all subsystem docs with a high-level overview.

#### [MODIFY] [GLOBAL_INDEX.md](file:///Users/marchansen/.gemini/GLOBAL_INDEX.md)

Register all new documentation files in the global index for easy access.

## Verification Plan

### Automated Verification

- **Link Check**: Verify all internal links between the new documentation files and the global index are functional.
- **Mermaid Validation**: Ensure all Mermaid diagrams render correctly (can be checked by viewing files).
- **Markdown Lint**: Run `markdownlint` on all new and modified documents.

### Manual Verification

- Review the content for technical accuracy against the source code.
- Ensure the descriptions are clear and follow the requested "detailed architecture" style.
