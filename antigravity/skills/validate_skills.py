"""
validate_skills.py — Antigravity skill spec compliance validator.

Checks all skills in ~/.gemini/antigravity/skills/ against the
spec rules from the Anthropic Complete Guide to Building Skills.

Usage:
    python3 validate_skills.py              # validate all skills
    python3 validate_skills.py code-review  # validate one skill
    python3 validate_skills.py --strict     # non-zero exit on any warning

Roadmap toward eval capability (future iterations):
  v1 (this version)
    - Structural compliance: naming, frontmatter fields, file layout
    - Static content checks: negative triggers, description length,
      word count, CHANGELOG presence, no XML in frontmatter
    - Machine-readable JSON output for CI integration

  v2 (planned)
    - LLM-as-judge description quality scoring: are trigger phrases
      specific enough? Would the agent route correctly?
    - Cross-skill conflict detection: flag description overlaps that
      would cause ambiguous routing between adjacent skills
    - Negative trigger coverage audit: for each skill, are there
      plausible queries that would incorrectly trigger it?

  v3 (planned)
    - Live triggering tests: run a set of probe queries through the
      agent and verify which skill loads (requires agent runtime)
    - Baseline comparison: measure response quality with vs. without
      a skill loaded (requires LLM judge + agent runtime)
    - Regression guard: block skill changes that degrade trigger
      accuracy below a threshold
"""

import sys
import re
import json
import pathlib
import argparse
from datetime import date

BASE = pathlib.Path.home() / '.gemini/antigravity/skills'
KEBAB = re.compile(r'^[a-z][a-z0-9-]+$')
TODAY = date.today().isoformat()


# ── Checks ────────────────────────────────────────────────────────────────────

def check_skill(skill_dir: pathlib.Path) -> dict:
    """
    Run all spec checks for a single skill directory.

    Returns a dict:
        {
          "skill": str,
          "errors": [str, ...],    # spec violations (must fix)
          "warnings": [str, ...],  # quality concerns (should fix)
          "info": [str, ...],      # informational notes
        }
    """
    errors = []
    warnings = []
    info = []
    name = skill_dir.name

    # ── 1. Folder naming ──────────────────────────────────────────────────────
    if not KEBAB.match(name):
        errors.append(
            f"Folder name '{name}' is not kebab-case "
            f"(must match ^[a-z][a-z0-9-]+$)"
        )
    if '_' in name:
        errors.append(
            f"Folder name '{name}' contains underscores — use hyphens"
        )
    if name.lower().startswith(('claude', 'anthropic')):
        errors.append(
            f"Folder name '{name}' uses reserved prefix (claude/anthropic)"
        )

    # ── 2. SKILL.md presence ──────────────────────────────────────────────────
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        errors.append("SKILL.md is missing")
        return _result(name, errors, warnings, info)

    content = skill_md.read_text(encoding='utf-8', errors='replace')

    # ── 3. YAML frontmatter ───────────────────────────────────────────────────
    if not content.startswith('---'):
        errors.append("SKILL.md is missing YAML frontmatter (must start with ---)")
        return _result(name, errors, warnings, info)

    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("SKILL.md frontmatter is not properly closed with ---")
        return _result(name, errors, warnings, info)

    fm_raw = parts[1]
    body = parts[2]

    # Parse top-level frontmatter fields (simple key: value lines)
    fm_fields = {}
    for line in fm_raw.splitlines():
        stripped = line.strip()
        if ':' in stripped and not stripped.startswith('-') and not stripped.startswith(' '):
            key, _, val = stripped.partition(':')
            fm_fields[key.strip()] = val.strip()

    # ── 4. name field ─────────────────────────────────────────────────────────
    name_val = fm_fields.get('name', '')
    if not name_val:
        errors.append("frontmatter: 'name' field is missing")
    else:
        if name_val != name:
            errors.append(
                f"frontmatter: name '{name_val}' does not match "
                f"folder name '{name}'"
            )
        if not KEBAB.match(name_val):
            errors.append(
                f"frontmatter: name '{name_val}' is not kebab-case"
            )

    # ── 5. description field ──────────────────────────────────────────────────
    # Description may span multiple lines with YAML block scalar (>)
    desc_lines = []
    in_desc = False
    for line in fm_raw.splitlines():
        if line.strip().startswith('description:'):
            in_desc = True
            rest = line.split(':', 1)[1].strip()
            if rest and rest != '>':
                desc_lines.append(rest)
        elif in_desc:
            # Block scalar lines start with whitespace
            if line and (line[0] == ' ' or line[0] == '\t'):
                desc_lines.append(line.strip())
            else:
                in_desc = False

    desc_val = ' '.join(desc_lines)

    if not desc_val:
        errors.append("frontmatter: 'description' field is missing")
    else:
        if len(desc_val) > 1024:
            errors.append(
                f"frontmatter: description is {len(desc_val)} chars (max 1024)"
            )
        if '<' in desc_val or '>' in desc_val:
            errors.append(
                "frontmatter: description contains XML angle brackets (not allowed)"
            )
        # Negative trigger check
        if not re.search(r'Do NOT|Do not', fm_raw + body[:600]):
            warnings.append(
                "No negative trigger found — add a 'Do NOT use for:' sentence "
                "in the description or the '## When to Use' section"
            )

    # ── 6. compatibility field ────────────────────────────────────────────────
    if 'compatibility' not in fm_fields:
        warnings.append(
            "'compatibility' field is missing — note network access, required "
            "tools, or 'No external tools required'"
        )

    # ── 7. metadata block ─────────────────────────────────────────────────────
    if 'metadata:' not in fm_raw:
        warnings.append(
            "'metadata:' block is missing — add author, version, category, tags"
        )
    else:
        for subkey in ('author', 'version', 'category', 'tags'):
            if subkey + ':' not in fm_raw:
                warnings.append(
                    f"metadata block is missing '{subkey}' subkey"
                )

    # ── 8. Forbidden top-level Gemini-specific fields ─────────────────────────
    gemini_fields = ['disable-model-invocation', 'allowed-tools',
                     'priority', 'type', 'labels', 'dependencies']
    for field in gemini_fields:
        # Only flag if they appear as top-level keys (not indented, i.e. inside metadata)
        for line in fm_raw.splitlines():
            if line.startswith(field + ':'):
                warnings.append(
                    f"Gemini-specific field '{field}' is at top level — "
                    f"move it into the metadata: block"
                )
                break

    # ── 9. XML angle brackets anywhere in frontmatter ────────────────────────
    if '<' in fm_raw or '>' in fm_raw:
        # Allow > in YAML block scalar indicator (e.g. "description: >")
        fm_no_scalars = re.sub(r':\s*>\s*$', ': ', fm_raw, flags=re.MULTILINE)
        if '<' in fm_no_scalars or re.search(r'>\s*\S', fm_no_scalars):
            errors.append(
                "frontmatter: contains XML angle brackets (not allowed outside "
                "block scalar indicators)"
            )

    # ── 10. Body quality ──────────────────────────────────────────────────────
    word_count = len(body.split())
    if word_count > 5000:
        warnings.append(
            f"SKILL.md body is {word_count} words (recommended max 5000) — "
            f"consider moving detailed reference content to references/"
        )
    if word_count < 30:
        warnings.append(
            f"SKILL.md body is only {word_count} words — likely incomplete"
        )
    else:
        info.append(f"Body: {word_count} words")

    # ── 11. README.md inside skill folder (not allowed) ───────────────────────
    if (skill_dir / 'README.md').exists():
        warnings.append(
            "README.md found inside skill folder — documentation should live "
            "in SKILL.md or references/; keep README.md at the repo root only"
        )

    # ── 12. Empty references/ or scripts/ directories ────────────────────────
    for subdir in ('references', 'scripts'):
        sd = skill_dir / subdir
        if sd.exists() and sd.is_dir():
            contents = [f for f in sd.iterdir() if not f.name.startswith('.')]
            if not contents:
                warnings.append(
                    f"{subdir}/ directory exists but is empty — "
                    f"add files or remove the directory"
                )

    # ── 13. CHANGELOG.md ─────────────────────────────────────────────────────
    if not (skill_dir / 'CHANGELOG.md').exists():
        warnings.append(
            "CHANGELOG.md is missing — add one with at least a [1.0.0] entry"
        )

    # ── 14. .venv inside skill folder ────────────────────────────────────────
    if (skill_dir / '.venv').exists():
        warnings.append(
            ".venv/ found inside skill folder — add it to a .gitignore "
            "and consider removing it from version control"
        )

    # ── 15. Description trigger quality (heuristic) ──────────────────────────
    use_phrases = ['Use when', 'use when', 'Use for', 'use for',
                   'when the user', 'when you need']
    has_use_phrase = any(p in desc_val for p in use_phrases)
    if desc_val and not has_use_phrase:
        warnings.append(
            "description lacks an explicit 'Use when...' phrase — "
            "add specific trigger conditions to improve routing accuracy"
        )

    return _result(name, errors, warnings, info)


def _result(name, errors, warnings, info):
    return {'skill': name, 'errors': errors, 'warnings': warnings, 'info': info}


# ── Output formatting ─────────────────────────────────────────────────────────

def print_report(results: list, strict: bool = False) -> int:
    """Print a human-readable report. Returns exit code."""
    total = len(results)
    error_count = sum(len(r['errors']) for r in results)
    warn_count = sum(len(r['warnings']) for r in results)
    fail_skills = [r for r in results if r['errors']]
    warn_skills = [r for r in results if r['warnings'] and not r['errors']]

    print()
    print('=' * 65)
    print(f'  Antigravity Skill Validator  —  {TODAY}')
    print(f'  {BASE}')
    print('=' * 65)

    for r in results:
        skill = r['skill']
        errs = r['errors']
        warns = r['warnings']
        infos = r['info']

        if errs:
            status = '[FAIL]'
        elif warns:
            status = '[WARN]'
        else:
            status = '[PASS]'

        detail = ''
        if infos:
            detail = f"  ({', '.join(infos)})"
        print(f'  {status} {skill}{detail}')

        for e in errs:
            print(f'         ✗ {e}')
        for w in warns:
            print(f'         ⚠ {w}')

    print()
    print('─' * 65)
    print(f'  {total} skills checked')
    print(f'  {error_count} errors  |  {warn_count} warnings')

    if error_count == 0 and warn_count == 0:
        print('  Result: ALL PASS')
        exit_code = 0
    elif error_count == 0:
        print('  Result: PASS WITH WARNINGS')
        exit_code = 1 if strict else 0
    else:
        print('  Result: FAILURES DETECTED')
        exit_code = 1

    print('=' * 65)
    print()
    return exit_code


def print_json(results: list) -> int:
    """Print machine-readable JSON. Returns exit code."""
    error_count = sum(len(r['errors']) for r in results)
    warn_count = sum(len(r['warnings']) for r in results)
    output = {
        'date': TODAY,
        'skills_checked': len(results),
        'error_count': error_count,
        'warning_count': warn_count,
        'pass': error_count == 0,
        'results': results,
    }
    print(json.dumps(output, indent=2))
    return 0 if error_count == 0 else 1


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Validate antigravity skill spec compliance'
    )
    parser.add_argument(
        'skill', nargs='?',
        help='Skill folder name to validate (default: all)'
    )
    parser.add_argument(
        '--strict', action='store_true',
        help='Exit non-zero on warnings as well as errors'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Output machine-readable JSON instead of human report'
    )
    args = parser.parse_args()

    if not BASE.exists():
        print(f'ERROR: skills directory not found: {BASE}', file=sys.stderr)
        sys.exit(1)

    # Non-skill directories to always skip
    SKIP_DIRS = {'evals', '__pycache__', '.git', 'node_modules'}

    if args.skill:
        skill_dir = BASE / args.skill
        if not skill_dir.exists():
            print(f'ERROR: skill not found: {skill_dir}', file=sys.stderr)
            sys.exit(1)
        skill_dirs = [skill_dir]
    else:
        skill_dirs = sorted(
            d for d in BASE.iterdir()
            if d.is_dir()
            and not d.name.startswith('.')
            and d.name not in SKIP_DIRS
        )

    results = [check_skill(d) for d in skill_dirs]

    if args.json:
        exit_code = print_json(results)
    else:
        exit_code = print_report(results, strict=args.strict)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
