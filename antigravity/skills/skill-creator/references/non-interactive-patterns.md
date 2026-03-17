# Non-Interactive Python Patterns

Reference for skill scripts that must work in both interactive terminals
and non-interactive environments (CI/CD, automated pipelines, `echo "" | script`).

Load this when a skill requires a Python/Bash script component and that
script will be run in automated environments.

---

## Core: Detect Non-Interactive Environment

```python
import sys
import os

def is_non_interactive():
    """Returns True when running in CI or without a terminal."""
    return (
        not sys.stdin.isatty() or
        os.getenv("CI") or
        os.getenv("GITHUB_ACTIONS") or
        os.getenv("AUTOMATED_MODE")
    )
```

---

## Core: Safe Input With Fallback

```python
def safe_input(prompt, default=None, choices=None, fallback_func=None):
    """input() that never crashes in non-interactive environments."""
    if is_non_interactive():
        if fallback_func:
            return fallback_func()
        if choices:
            return choices[0]
        return default or "auto"

    try:
        response = input(prompt).strip()
        if choices and response not in choices:
            print(f"Invalid choice. Options: {choices}")
            return safe_input(prompt, default, choices, fallback_func)
        return response if response else default
    except (EOFError, KeyboardInterrupt):
        return default or "interrupted"
```

---

## Anti-Patterns to Avoid

```python
# ❌ Crashes in CI with "EOFError: EOF when reading a line"
choice = input("Deploy to staging or production? ")

# ✅ Graceful in any environment
choice = safe_input("Deploy to staging or production? ",
                    choices=["staging", "production"],
                    default="staging")
```

```python
# ❌ Hardcoded relative path — breaks when called from other directories
config = open("./config.yaml")

# ✅ Always resolves relative to the script itself
from pathlib import Path
config = open(Path(__file__).parent / "config" / "defaults.yaml")
```

---

## Script Structure Template

```python
#!/usr/bin/env python3
"""skill-name — one-line description."""

import sys
import os
import argparse
from pathlib import Path


def is_non_interactive():
    return (not sys.stdin.isatty() or os.getenv("CI") or
            os.getenv("GITHUB_ACTIONS") or os.getenv("AUTOMATED_MODE"))


def safe_input(prompt, default=None, choices=None):
    if is_non_interactive():
        return choices[0] if choices else (default or "auto")
    try:
        r = input(prompt).strip()
        if choices and r not in choices:
            print(f"Options: {choices}")
            return safe_input(prompt, default, choices)
        return r if r else default
    except (EOFError, KeyboardInterrupt):
        return default


def main():
    parser = argparse.ArgumentParser(description="skill-name")
    parser.add_argument("--non-interactive", action="store_true")
    args = parser.parse_args()

    try:
        run(args)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run(args):
    if is_non_interactive():
        # Auto-select defaults, no prompts
        pass
    else:
        # Interactive prompts and confirmations
        pass


if __name__ == "__main__":
    main()
```

---

## Testing Non-Interactive Behaviour

```bash
# Simulate CI — should never hang or crash
echo "" | python scripts/my_skill.py

# With explicit CI flag
CI=true python scripts/my_skill.py

# Unit test pattern
with patch("sys.stdin.isatty", return_value=False):
    result = safe_input("prompt", default="fallback")
    assert result == "fallback"
```

---

## Skill Categories and Their Requirements

| Category | Non-interactive requirement | Typical use |
|---|---|---|
| finalization | Mandatory — called in automated workflows | End-of-session cleanup |
| initialization | Strongly recommended | Pre-flight checks |
| utility | Adapt based on context | General-purpose tools |

Finalization skills must never block. Always return or auto-approve in
non-interactive mode rather than waiting for input.
