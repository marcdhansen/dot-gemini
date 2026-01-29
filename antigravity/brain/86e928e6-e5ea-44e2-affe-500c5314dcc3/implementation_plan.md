# Update GitHub Link and Project Name References

Update all internal links and name references to point to the new forked repository `https://github.com/marcdhansen/LightRAG_gemini` and reflect the project name `LightRAG_gemini`.

## Proposed Changes

### [Web UI Component]

#### [MODIFY] [constants.ts](file:///Users/marchansen/claude_test/LightRAG/lightrag_webui/src/lib/constants.ts)
- Already updated in previous step. Updated `SiteInfo.name` and `SiteInfo.github`.

### [Core Components]

#### [MODIFY] [pyproject.toml](file:///Users/marchansen/claude_test/LightRAG/pyproject.toml)
- Update GitHub URLs in `[project.urls]` section.

#### [MODIFY] [__init__.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/__init__.py)
- Update `__url__` to point to the new repository.

#### [MODIFY] [exceptions.py](file:///Users/marchansen/claude_test/LightRAG/lightrag/exceptions.py)
- Update the help URL in `StorageNotInitializedError`.

### [Documentation]

#### [MODIFY] [README.md](file:///Users/marchansen/claude_test/LightRAG/README.md)
- Update all occurrences of `HKUDS/LightRAG` to `marcdhansen/LightRAG_gemini`.
- Update the project name to `LightRAG_gemini` where appropriate.

#### [MODIFY] [README-zh.md](file:///Users/marchansen/claude_test/LightRAG/README-zh.md)
- Update all occurrences of `HKUDS/LightRAG` to `marcdhansen/LightRAG_gemini`.

## Verification Plan

### Automated Tests
- Run `grep -r "HKUDS/LightRAG" .` to ensure all occurrences are updated (excluding third-party references or historical notes if any).

### Manual Verification
- Verify the Web UI GitHub link icon (already done via code review).
- Verify that the README looks correct.
