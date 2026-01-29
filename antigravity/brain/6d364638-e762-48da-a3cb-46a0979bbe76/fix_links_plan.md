# Standardize Global Index Links

## Goal

Fix broken or unreliable links in `GLOBAL_INDEX.md` by standardizing on absolute `file://` URIs.

## Proposed Changes

### [GLOBAL CONFIG]

#### [MODIFY] [GLOBAL_INDEX.md](../../../../.gemini/GLOBAL_INDEX.md)

* Convert all relative links to absolute `file://` URIs.
* Ensure all absolute paths are prefixed with `file://`.
* Verify links to key rules (`GEMINI.md`, etc.), projects (`LightRAG`), and skills.

## Verification Plan

1. Verify file existence for every new URI using `ls`.
2. Provide the updated file to the user and request confirmation that they are clickable.
