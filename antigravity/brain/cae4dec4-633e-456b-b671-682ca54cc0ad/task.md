# Key-Value Entity Extraction Implementation

## Tasks

- [x] Add key-value prompts to `prompt.py`
  - [x] Add `entity_extraction_system_prompt_key_value`
  - [x] Add `entity_extraction_user_prompt_key_value`
- [x] Add YAML parser to `operate.py`
  - [x] Create `_parse_yaml_extraction()` function
  - [x] Integrate with existing extraction flow
- [x] Add configuration to `.env`
- [x] Verify implementation
  - [x] Restart server with `EXTRACTION_FORMAT=key_value`
  - [x] Upload test document
  - [x] Check knowledge graph for clean entity names ✅
