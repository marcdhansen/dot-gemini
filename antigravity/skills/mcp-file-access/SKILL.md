---
name: mcp-file-access
description: >
  Reference guide for file reading and writing in this Claude Desktop
  setup: which MCP tools exist, what paths they can reach, and the correct
  approach for each case. Use when starting any session that involves
  touching files, or when uncertain which tool to use for a given path.
  Do NOT use as a general programming reference; this skill is specific
  to the filesystem and mac-shell MCP configuration on this machine.
compatibility: >
  Specific to Claude Desktop with @modelcontextprotocol/server-filesystem
  and github:cfdude/mac-shell-mcp configured. Allowed filesystem paths:
  ~/.agent, ~/.gemini, ~/Desktop, ~/Documents, ~/Downloads.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: infrastructure
  tags: [mcp, filesystem, file-access, claude-desktop, tooling]
---

# Skill: mcp-file-access

**Purpose**: Documents exactly how file reading and writing works in this Claude Desktop
setup — which tools exist, what they can reach, and the correct approach for each case.

*Read this before touching any file in a new session.*

---

## The Two MCP Tools and What They Can Reach

| Tool | Underlying server | Can reach |
|------|------------------|-----------|
| `filesystem:*` | `@modelcontextprotocol/server-filesystem` | `~/.agent`, `~/.gemini`, `~/Desktop`, `~/Documents`, `~/Downloads` |
| `mac-shell:execute_command` | `github:cfdude/mac-shell-mcp` | Anything on the Mac the user account can access |

Config lives at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

To add or remove directories from the filesystem server, edit the `args` array and restart Claude Desktop:
```json
"args": ["-y", "@modelcontextprotocol/server-filesystem",
         "/Users/marchansen/.agent",
         "/Users/marchansen/.gemini",
         "/Users/marchansen/Desktop",
         "/Users/marchansen/Documents",
         "/Users/marchansen/Downloads"]
```

---

## Reading Files

Use `filesystem:read_text_file` for anything in the allowed directories — including `~/.agent/`:

```
filesystem:read_text_file  path=/Users/marchansen/.agent/AGENTS.md
```

For **paths with spaces** (e.g. the config file itself), use a small Python script via mac-shell:
```python
# filesystem:write_file  path=/Users/marchansen/Documents/_read.py
import pathlib
p = pathlib.Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
print(p.read_text())
```
Then: `mac-shell:execute_command  command=python3.10  args=["/Users/marchansen/Documents/_read.py"]`

---

## Writing Files to `~/.agent/`

`filesystem:write_file` works directly — no bridge needed:

```
filesystem:write_file
  path: /Users/marchansen/.agent/docs/sop/SOMEFILE.md
  content: |
    # Content here
    ...
```

For **multi-file writes or complex transforms**, it's still cleaner to write a Python
script and run it, but this is a style choice, not a requirement.

---

## Patching Existing Files in `~/.agent/`

Use `filesystem:edit_file` for targeted line replacements:

```
filesystem:edit_file
  path: /Users/marchansen/.agent/docs/phases/01_session_context.md
  edits:
    - oldText: "- [ ] Review previous session context"
      newText: "- [ ] **Read prior handoff first**\n- [ ] Review previous session context"
```

For **large or complex patches** (multiple anchors, assert guards), write a Python script:

```python
# filesystem:write_file  path=/Users/marchansen/Documents/_patch.py
import pathlib

p = pathlib.Path("/Users/marchansen/.agent/docs/phases/01_session_context.md")
text = p.read_text()

OLD = "- [ ] Review previous session context"
NEW = "- [ ] **Read prior handoff first**\n- [ ] Review previous session context"

assert OLD in text, f"Anchor not found — file may have changed"
assert NEW not in text, "Already patched"
p.write_text(text.replace(OLD, NEW, 1))
print("patched")
```

The `assert` guards prevent silent no-ops when anchors have drifted or patches were
already applied.

---

## mac-shell Command Whitelist

**The whitelist resets between Claude Desktop sessions** — commands must be re-added
each session.

**Always add at the start of any session that runs scripts:**
```
mac-shell:add_to_whitelist  command=python3.10  securityLevel=safe
```

Use `mac-shell:get_whitelist` to check what's currently available.

Default safe commands (usually pre-populated):
`ls`, `cat`, `find`, `grep`, `pwd`, `echo`, `head`, `tail`, `wc`, `cd`

Commands to add when needed:
`python3.10` (safe), `bash` (requires_approval), `mkdir` (requires_approval)

`bash` requires human approval per-invocation — prefer `python3.10` scripts for automation.

---

## Paths With Spaces

`mac-shell` splits args on spaces, so paths containing spaces (e.g. `~/Library/Application Support/...`)
must be accessed via a Python script written to `~/Documents/` first. See Reading Files above.

`filesystem:*` tools handle spaces in paths natively — no workaround needed.

---

## Quick Reference

| Goal | Tool | Notes |
|------|------|-------|
| Read any allowed file | `filesystem:read_text_file` | Direct; handles spaces in paths |
| Read path with spaces via mac-shell | Write + run reader `.py` | Only needed for mac-shell, not filesystem tools |
| Write to `~/.agent/` | `filesystem:write_file` | Direct — no bridge needed |
| Patch file in `~/.agent/` | `filesystem:edit_file` | For simple replacements |
| Patch file with assert guards | Write patch `.py` → `python3.10` | For complex multi-anchor patches |
| Read `claude_desktop_config.json` | Write + run reader `.py` | Path has a space |
| Add filesystem directory | Edit config, restart Claude Desktop | See config snippet above |

---

## Config File Location

`~/Library/Application Support/Claude/claude_desktop_config.json`

Path contains a space — use the reader-script pattern (mac-shell) or `filesystem:write_file`
+ `python3.10` to read it programmatically.

---

*Last updated: 2026-03-15*
*~/.agent added to filesystem MCP server — write-via-bridge pattern no longer required.*
