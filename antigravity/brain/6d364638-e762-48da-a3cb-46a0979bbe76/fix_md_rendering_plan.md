# Resolve Markdown Rendering & Standardize Linting

## Goal

Fix "literal text" rendering in `GLOBAL_INDEX.md` and ensure systemic markdown quality by integrating `markdownlint` into the Standard Mission Protocol (SMP).

## Proposed Changes

### [GLOBAL CONFIG]

#### [MODIFY] [GLOBAL_INDEX.md](../../../../.gemini/GLOBAL_INDEX.md)

* **Fix Rendering**: Use relative paths for local files (e.g., `GEMINI.md`) instead of absolute `file:///` URIs.
* **Standardize Indentation**: Use 2 spaces for nested lists (GFM standard).
* **Fix MD013**: Allow long lines for links if necessary, or wrap them.

#### [MODIFY] [GEMINI.md](../../../../.gemini/GEMINI.md)

* Update **PFC** to include a check for `markdownlint`.
* Update **RTB** to explicitly mandate `markdownlint` on all modified markdown files.

#### [NEW] [.markdownlint.json](../../../../.gemini/.markdownlint.json)

* Configure rules to ignore `MD013` (line length) specifically for links, or just globally for documentation consistency.

## Verification Plan

1. Run `markdownlint GLOBAL_INDEX.md` and ensure zero errors.
2. Provide the file to the user and request confirmation that links are rendered correctly.
