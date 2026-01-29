# Walkthrough: YAML Key-Value Extraction Format

## Problem
Entity extraction using smaller LLMs (e.g., `qwen2.5-coder:1.5b`) produced corrupted entity names like `#>LightRAG.<[#` due to difficulties with the delimiter-based output format.

## Solution
Implemented a simpler YAML-style output format that smaller LLMs can produce reliably.

## Changes Made

### 1. [prompt.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/prompt.py)
Added two new prompts:
- `entity_extraction_system_prompt_key_value`
- `entity_extraction_user_prompt_key_value`

### 2. [operate.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/operate.py)
Added `_parse_yaml_extraction()` function to parse YAML output and integrated it into `_process_extraction_result()`.

### 3. [.env](file:///Users/marchansen/claude_test/LightRAG/.env)
Added `EXTRACTION_FORMAT=key_value` configuration.

## Verification

![Clean entity names in Knowledge Graph](/Users/marchansen/.gemini/antigravity/brain/cae4dec4-633e-456b-b671-682ca54cc0ad/clean_entity_names_list_1769059967830.png)

Entity names are now clean and properly formatted:
- `LightRAG System`
- `Antigravity`
- `Neo4j`
- `RAG (Retrieval-Augmented Generation)`
- `RAGAS`
- `qwen2.5-coder:1.5b`

## Result
✅ **SUCCESS** - No corrupted labels in the knowledge graph.
