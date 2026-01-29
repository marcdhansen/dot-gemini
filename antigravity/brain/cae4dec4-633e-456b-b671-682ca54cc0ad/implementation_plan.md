# Key-Value Entity Extraction Format

Implement a simpler YAML-like output format for entity/relationship extraction to improve reliability with smaller LLMs like `qwen2.5-coder:1.5b`.

## Problem Statement

The current extraction format uses complex delimiters (`<|#|>`) that smaller models struggle to produce consistently:
```
entity<|#|>LightRAG<|#|>Organization<|#|>A RAG system
relation<|#|>LightRAG<|#|>Users<|#|>serves<|#|>LightRAG serves users
```

This leads to malformed entity names like `#>LightRAG.< [#` appearing in the knowledge graph.

## Proposed Solution

Use a simpler YAML-like key-value format that smaller models handle reliably:

```yaml
entities:
  - name: LightRAG
    type: Organization
    description: A RAG system for knowledge graphs

  - name: Users
    type: Person
    description: People who use the system

relationships:
  - source: LightRAG
    target: Users
    keywords: serves, provides
    description: LightRAG serves users with RAG capabilities
```

---

## Proposed Changes

### Component 1: Prompts

#### [MODIFY] [prompt.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/prompt.py)

Add two new prompts after the existing extraction prompts (~line 183):

1. **`entity_extraction_system_prompt_key_value`** - System instructions for YAML-style output
2. **`entity_extraction_user_prompt_key_value`** - User prompt template for YAML-style extraction

Key design choices:
- Use standard YAML syntax (simpler than custom delimiters)
- Clear section headers (`entities:` and `relationships:`)
- Explicit field names (`name`, `type`, `description`, `source`, `target`, `keywords`)
- Keep `{completion_delimiter}` for end-of-output signal

---

### Component 2: Parser

#### [MODIFY] [operate.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/operate.py)

Add a YAML parser function to convert key-value output to internal format:

1. **Add `_parse_key_value_extraction()`** function (~line 380):
   - Parse YAML output from LLM
   - Convert to same dict structure as native format
   - Handle malformed YAML gracefully with fallback

2. **Modify `_process_extraction_result()`** to detect and route key-value format

---

### Component 3: Configuration

#### [MODIFY] [.env](file:///Users/marchansen/claude_test/LightRAG/.env)

Add configuration option (commented by default):
```bash
### Entity extraction output format: native, key_value
### key_value recommended for smaller LLMs (< 7B parameters)
# EXTRACTION_FORMAT=key_value
```

---

## Verification Plan

### Automated Tests

1. **Unit test for parser**: Create test cases with sample YAML output
2. **Integration test**: Process a test document with `EXTRACTION_FORMAT=key_value`

### Manual Verification

1. Set `EXTRACTION_FORMAT=key_value` in `.env`
2. Restart LightRAG server
3. Clear existing data and re-upload `small_test.txt`
4. Verify knowledge graph shows clean entity names (no `#`, `<|`, etc.)
5. Query the system to confirm entities/relationships work correctly
