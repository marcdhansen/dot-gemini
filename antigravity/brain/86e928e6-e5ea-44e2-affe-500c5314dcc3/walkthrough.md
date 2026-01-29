# Walkthrough: Update GitHub Link and Project Name

I have updated the project references to point to the new forked repository and reflect the updated project name `LightRAG_gemini`.

## Changes Made

### Web UI
- Updated `lightrag_webui/src/lib/constants.ts` to change the site name to `LightRAG_gemini` and the GitHub link to `https://github.com/marcdhansen/LightRAG_gemini`.
- Updated `lightrag_webui/package.json` name to `lightrag_gemini-webui`.
- Performed a bulk replacement of `LightRAG` with `LightRAG_gemini` in all locale files (`en.json`, `zh.json`, etc.) and `LoginPage.tsx`.

### Core Python Code
- Updated `lightrag/__init__.py` to change `__url__` to the new forked repo.
- Updated `lightrag/exceptions.py` to fix the help URL in `StorageNotInitializedError`.
- Updated `pyproject.toml` to point all project URLs (Homepage, Repository, etc.) to the new forked repo.

### Documentation
- Replaced all occurrences of `HKUDS/LightRAG` with `marcdhansen/LightRAG_gemini` in the following files:
  - `README.md`
  - `README-zh.md`
  - `docs/DockerDeployment.md`
  - `docs/FrontendBuildGuide.md`
  - `docs/OfflineDeployment.md`
  - `lightrag/api/README.md`
  - `lightrag/api/README-zh.md`
  - `lightrag/tools/check_initialization.py`
  - `lightrag/tools/download_cache.py`
  - `lightrag/kg/postgres_impl.py`
  - `lightrag/tools/lightrag_visualizer/README.md`

## Verification Results

### GitHub Link Check
I verified that the GitHub link in the UI and documentation now points to `https://github.com/marcdhansen/LightRAG_gemini`.

### Name Consistency
The Web UI now consistently uses `LightRAG_gemini` in titles, labels, and descriptions across different languages.

```bash
# Verification command used:
grep -r "HKUDS/LightRAG" .
# Output: No results found.
```
