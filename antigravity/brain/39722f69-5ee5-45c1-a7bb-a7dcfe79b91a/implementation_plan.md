# ACE Phase 3 & Graph Visualization Verification

This plan covers the expansion of the ACE (Agentic Context Evolution) framework to support automated graph repair and the verification of the graph visualization feature in the WebUI.

## Proposed Changes

### ACE Phase 3: Automated Graph Repair [NEW]

Implementation of the Reflector and Curator logic for identifying and fixing graph hallucinations.

#### [MODIFY] [reflector.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/ace/reflector.py)

- Implement `reflect_graph_issues(self, query: str, generation_result: Dict[str, Any]) -> List[Dict[str, Any]]`.
- Add prompt logic to identify "hallucination by proximity" (like the Beekeeper/Heart Disease case).

#### [MODIFY] [curator.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/ace/curator.py)

- Implement `apply_repairs(self, repairs: List[Dict[str, Any]])`.
- Integrated with `LightRAG` deletion utilities to prune incorrect edges/nodes.

#### [MODIFY] [core.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/core.py)

- Add `adelete_entity` and `adelete_relation` wrapper methods.
- Update `aquery` (or create a dedicated `aquery_ace`) to optionally trigger the ACE reflection/repair loop.

#### [MODIFY] [api/main.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/lightrag/api/main.py)

- (TBD) Add endpoints to trigger graph reflection and repair if not already covered by the ACE core loop.

---

### Graph Visualization & Construction Verification

#### [EXTRACT] [beekeeping_test_data](file:///Users/marchansen/antigravity_lightrag/LightRAG/docs/beekeeping_test_data.txt)

- Extract key beekeeping examples from the LightRAG PDF to use as a gold standard.

#### [VERIFY] [test_graph_visualization.py](file:///Users/marchansen/antigravity_lightrag/LightRAG/tests/ui/test_graph_visualization.py)

- Run the existing Playwright test.
- Add a new test case for the beekeeping dataset visualization.

#### [COMPARE] [graph_construction_comparison](file:///Users/marchansen/.gemini/antigravity/brain/39722f69-5ee5-45c1-a7bb-a7dcfe79b91a/graph_comparison.md)

- Research Neo4j's knowledge graph construction for the same test data.
- Analyze differences in entity extraction, relationship typing, and graph density between LightRAG, Neo4j, and MemGraph.

#### [NEW] [Manual Verification]

- Launch the WebUI and verify the Beekeeping graph rendering.
- Test "Hybrid" vs "Low-level" vs "High-level" searches on the beekeeping data.

## Verification Plan

### Automated Tests

- Run Playwright tests:

  ```bash
  pytest tests/ui/test_graph_visualization.py
  ```

- Run unit tests for Reflector/Curator (to be created):

  ```bash
  pytest tests/test_ace_repair.py
  ```

### Manual Verification

1. Start LightRAG server: `uv run lightrag-server`.
2. Open WebUI in browser.
3. Upload a sample document.
4. Go to Knowledge Graph tab and verify rendering.
5. Execute a query that triggers ACE reflection and verify the playbook is updated.
