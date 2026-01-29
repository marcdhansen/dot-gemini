# LightRAG Enhancement Planning

## Objective
Transform TODO.md items into a concrete implementation plan for the LightRAG enhancement project.

## Planning Phase
- [x] Review existing TODO.md items
- [x] Understand priority system (p0 = highest, p1 = next)
- [x] Research ACE framework architecture
- [x] Create agent memory with project context
- [x] Create prioritized implementation plan
- [x] Get user approval on plan

## Implementation Roadmap (To be refined)
- [ ] **Phase 1: Core System Stability** (p0)
  - [ ] Ensure BCBC PDF processing works end-to-end
  - [ ] Verify graph creation and query handling
  
- [ ] **Phase 2: Evaluation Framework** (Early)
  - [ ] Integrate RAGAS for evaluation
  - [ ] Set up Langfuse for tracing
  
- [ ] **Phase 5: Browser Compatibility (Safari)**
  - [/] Investigate Safari rendering regression ([lightrag-h7x](bd://lightrag-h7x))
    - [x] Create beads issue
    - [ ] Compare current code with known working state (git history)
    - [ ] Identify breaking CSS/JS change
  - [ ] Implement and verify fixes
  
- [ ] **Phase 3: ACE Framework Integration**
  - [x] Diagnose blank UI issue
- [x] Build and restore WebUI
    - [x] Identify missing `dist` folder
    - [x] Run `bun run build` in `lightrag_webui`
- [x] Restart LightRAG server
- [x] Verify UI functionality via browser
    - [x] Confirm Dark Mode availability
  
- [ ] **Phase 4: Enhancements**
  - [ ] MCP integration (client + server)
  - [ ] Keyword search support
  - [ ] Citation links in query responses
