#!/usr/bin/env python3
"""
trigger_eval.py — Skill routing evaluation for Ollama models.

Tests whether each model correctly routes a user query to the right skill,
or returns "none" when no skill applies. Runs models from smallest to largest.

Usage:
    python3 trigger_eval.py                         # all models, all cases
    python3 trigger_eval.py --models llama3.2:3b    # specific model(s)
    python3 trigger_eval.py --cases trigger_cases.yaml
    python3 trigger_eval.py --category positive     # filter by category
    python3 trigger_eval.py --fast                  # skip models >5GB
    python3 trigger_eval.py --json results.json     # save full results
    python3 trigger_eval.py --dry-run               # show prompt, don't call API

Architecture:
    1. Load skill metadata from SKILL.md frontmatter (Level 1 — what the
       agent actually sees in its system prompt).
    2. Build a routing prompt: skill list + user query.
    3. Call Ollama chat API, parse the response to extract a skill name.
    4. Score: correct / wrong / unparseable.
    5. Print per-model table + cross-model comparison.

Response parsing strategy (most to least strict):
    1. Exact match against valid skill names (case-insensitive)
    2. First token of response matches a skill name
    3. Any valid skill name appears anywhere in the response
    4. "none" / "no skill" / "n/a" variants
    5. → unparseable (counted as wrong)
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
import pathlib
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

SKILLS_DIR = pathlib.Path.home() / ".gemini/antigravity/skills"
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_CASES = pathlib.Path(__file__).parent / "trigger_cases.yaml"
TIMEOUT_SECS = 120  # 2 min per call — allows for cold model load on first request

# Models ordered smallest → largest (non-embedding, non-reranker).
# Code-specialized models are included but marked; they may underperform
# on routing tasks since they're tuned for generation, not classification.
MODELS_ORDERED = [
    # ~400 MB
    ("qwen2.5:0.5b",          0.40, "general"),
    ("qwen2.5-coder:0.5b",    0.40, "code"),
    # ~500 MB
    ("qwen3:0.6b",            0.52, "general"),
    ("granite4:350m",         0.71, "general"),
    # ~800-900 MB
    ("deepseek-coder:1.3b",   0.78, "code"),
    ("gemma3:1b",             0.82, "general"),
    ("granite3-moe:1b",       0.82, "general"),
    ("yi-coder:1.5b",         0.87, "code"),
    ("qwen2.5-coder:1.5b",    0.99, "code"),
    # ~1-1.5 GB
    ("deepseek-r1:1.5b",      1.1,  "general"),
    ("granite3.1-moe:1b",     1.4,  "general"),
    # ~1.5-2 GB
    ("granite3.1-dense:2b",   1.6,  "general"),
    ("qwen2.5-coder:3b",      1.9,  "code"),
    ("llama3.2:3b",           2.0,  "general"),
    ("granite3.1-moe:3b",     2.0,  "general"),
    ("granite4:3b",           2.1,  "general"),
    ("granite4:1b",           3.3,  "general"),  # reported 1b but 3.3GB — unusual
    # ~4 GB
    ("codellama:7b",          3.8,  "code"),
    ("deepseek-coder:6.7b",   3.8,  "code"),
    ("starcoder2:7b",         4.0,  "code"),
    ("dolphin-mistral:7b",    4.1,  "general"),
    ("dolphincoder:7b",       4.2,  "code"),
    ("mistral:7b",            4.4,  "general"),
    ("llama3:8B",             4.7,  "general"),
    ("qwen2.5-coder:7b",      4.7,  "code"),
    ("deepseek-r1:7b",        4.7,  "general"),
    ("llama3-groq-tool-use:8B", 4.7, "general"),
    ("qwen2.5:7b-instruct",   4.7,  "general"),
    ("llama3.1:8B",           4.9,  "general"),
    ("yi-coder:9b",           5.0,  "code"),
    # ~7+ GB
    ("mistral-nemo:latest",   7.1,  "general"),
    ("qwen2.5-coder:14b",     9.0,  "code"),
    ("dolphincoder:15b",      9.1,  "code"),
    ("gpt-oss:20b",           13.0, "general"),
]


# ── YAML parser (no pyyaml dependency) ───────────────────────────────────────

def parse_yaml_cases(path: pathlib.Path) -> list:
    """
    Minimal YAML parser for the trigger_cases.yaml format.
    Handles the specific structure used — does not attempt general YAML.
    """
    text = path.read_text(encoding="utf-8")
    cases = []
    current = {}
    in_cases = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped == "cases:":
            in_cases = True
            continue
        if not in_cases:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("- name:"):
            if current.get("name"):
                cases.append(current)
            current = {"name": stripped[len("- name:"):].strip()}
        elif stripped.startswith("name:") and current:
            current["name"] = stripped[len("name:"):].strip()
        elif stripped.startswith("input:"):
            val = stripped[len("input:"):].strip()
            current["input"] = val.strip('"').strip("'")
        elif stripped.startswith("expected:"):
            current["expected"] = stripped[len("expected:"):].strip()
        elif stripped.startswith("category:"):
            current["category"] = stripped[len("category:"):].strip()

    if current.get("name"):
        cases.append(current)

    return cases


# ── Skill metadata loader ──────────────────────────────────────────────────────

def load_skill_metadata(skills_dir: pathlib.Path) -> list:
    """
    Load Level 1 metadata (name + description) from all SKILL.md files.
    Returns list of (name, description) tuples, sorted by name.
    This is exactly what the agent sees in its system prompt.
    """
    skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        # Skip the evals directory itself
        if skill_dir.name == "evals":
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm = parts[1]
        name = ""
        desc_lines = []
        in_desc = False
        for line in fm.splitlines():
            s = line.strip()
            if s.startswith("name:"):
                name = s[5:].strip()
            elif s.startswith("description:"):
                in_desc = True
                rest = s[12:].strip()
                if rest and rest != ">":
                    desc_lines.append(rest)
            elif in_desc:
                if line and (line[0] in (" ", "\t")):
                    desc_lines.append(s)
                else:
                    in_desc = False
        if name:
            desc = " ".join(desc_lines).strip()
            # Truncate very long descriptions for the prompt
            if len(desc) > 200:
                desc = desc[:197] + "..."
            skills.append((name, desc))
    return skills


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_system_prompt(skills: list) -> str:
    """
    Build the routing system prompt from skill metadata.
    Kept concise and unambiguous for small models.
    Includes few-shot examples to ground the expected output format.
    """
    skill_list = "\n".join(
        f"  {name}: {desc}" for name, desc in skills
    )
    valid_names = ", ".join(name for name, _ in skills)
    return f"""You are a skill routing system. Your only job is to read a user message and output the name of the most relevant skill.

RULES:
- Output ONLY a single skill name from the list below, or the word "none"
- Do not explain, do not add punctuation, do not add any other text
- If no skill is relevant to the user message, output exactly: none
- Do not answer the user's question. Only output the skill name.

VALID SKILL NAMES:
{valid_names}

SKILL DESCRIPTIONS:
{skill_list}

EXAMPLES:
User: I need to push my code and write a commit message
Output: git

User: Walk me through closing out this session
Output: finalization

User: I need to understand the impact before I change this module
Output: planning

User: Can you look at this code before I merge it?
Output: code-review

User: I'm ready to open a PR for my feature
Output: pull-request

User: Where is the login function implemented?
Output: code-search

User: Which files reference the payment module?
Output: code-search

User: Give me a briefing before we start
Output: session-briefing

User: Run the CI pipeline
Output: cicd

User: Clean up the Playwright browser tabs
Output: playwright-manager

User: What is the capital of France?
Output: none

User: Write a Python function that reverses a string
Output: none

User: Implement a sorting algorithm for me
Output: none

User: Good morning!
Output: none"""


# ── Response parser ───────────────────────────────────────────────────────────

NONE_PATTERNS = re.compile(
    r"^(none|no skill|no match|n/a|not applicable|no relevant|does not match)$",
    re.IGNORECASE,
)

# Known model misspellings: map to the correct skill name.
# Checked against the full valid_names set before use.
KNOWN_MISSPELLINGS = {
    "retropective":   "retrospective",
    "retrospecive":   "retrospective",
    "retrospetive":   "retrospective",
    "intialization":  "session-briefing",
    "initialisation": "session-briefing",
    "devil-advocate": "devils-advocate",
    "beads_manager":  "beads-manager",
    "code_review":    "code-review",
    "code_navigation": "code-search",
}


def parse_response(raw: str, valid_names: set) -> str:
    """
    Extract a skill name or "none" from a model response.
    Returns the matched skill name, "none", or "UNPARSEABLE".
    """
    # Clean up common model artifacts
    text = raw.strip()
    text = re.sub(r"[`*_]", "", text)   # strip markdown
    text = text.strip("\"'.,;:")         # strip punctuation wrapping
    text = text.strip()

    # 1. Exact match (handles "git", "code-review", "none", etc.)
    lower = text.lower()
    if lower in valid_names:
        return lower
    if NONE_PATTERNS.match(lower):
        return "none"

    # 1b. Known misspellings (e.g. "retropective" → "retrospective")
    corrected = KNOWN_MISSPELLINGS.get(lower)
    if corrected and corrected in valid_names:
        return corrected

    # 2. First word/token
    first = re.split(r"[\s\n,.(]", text)[0].strip().lower().rstrip(".,;:")
    if first in valid_names:
        return first
    if NONE_PATTERNS.match(first):
        return "none"

    # 3. Any valid name anywhere in the response
    for name in sorted(valid_names, key=len, reverse=True):  # longest first
        if re.search(r"\b" + re.escape(name) + r"\b", lower):
            return name

    # 4. "none" variants anywhere
    if re.search(r"\bnone\b|\bno skill\b|\bn/a\b", lower):
        return "none"

    return "UNPARSEABLE"


# ── Ollama API caller ─────────────────────────────────────────────────────────

def call_ollama(model: str, system_prompt: str, user_message: str) -> str:
    """
    Call the Ollama chat API. Returns the model's text response.
    Raises on connection error or non-200 response.
    """
    payload = json.dumps({
        "model": model,
        "stream": False,
        "options": {
            "temperature": 0.0,   # deterministic
            "num_predict": 32,    # we only need a skill name — keep it short
        },
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECS) as resp:
        data = json.loads(resp.read())
    return data["message"]["content"]


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_result(parsed: str, expected: str) -> str:
    """Return 'correct', 'wrong', or 'unparseable'."""
    if parsed == "UNPARSEABLE":
        return "unparseable"
    if parsed == expected.lower():
        return "correct"
    return "wrong"


# ── Runner ────────────────────────────────────────────────────────────────────

def run_eval(
    models: list,
    cases: list,
    skills: list,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Run the full eval. Returns results dict keyed by model name.
    """
    system_prompt = build_system_prompt(skills)
    valid_names = {name.lower() for name, _ in skills} | {"none"}

    all_results = {}

    for model_name, size_gb, model_type in models:
        print(f"\n{'─'*65}")
        size_label = f"{size_gb:.1f}GB"
        print(f"  Model: {model_name}  ({size_label}, {model_type})")
        print(f"{'─'*65}")

        if dry_run:
            print("  [DRY RUN — showing prompt for first case only]")
            print()
            print("  SYSTEM PROMPT:")
            for line in system_prompt.splitlines()[:8]:
                print(f"    {line}")
            print("    ...")
            print()
            print(f"  USER: {cases[0]['input']}")
            print(f"  EXPECTED: {cases[0]['expected']}")
            break

        model_results = []
        correct = wrong = unparseable = 0
        by_category = {}

        for case in cases:
            name = case["name"]
            query = case["input"]
            expected = case["expected"].lower()
            category = case.get("category", "positive")

            try:
                start = time.time()
                raw = call_ollama(model_name, system_prompt, query)
                elapsed = time.time() - start
                parsed = parse_response(raw, valid_names)
                outcome = score_result(parsed, expected)
            except urllib.error.URLError as e:
                print(f"  [ERROR] Ollama not reachable: {e}")
                print("  Is Ollama running? Try: ollama serve")
                sys.exit(1)
            except Exception as e:
                raw = f"ERROR: {e}"
                parsed = "UNPARSEABLE"
                outcome = "unparseable"
                elapsed = 0.0

            if outcome == "correct":
                correct += 1
            elif outcome == "wrong":
                wrong += 1
            else:
                unparseable += 1

            cat_stats = by_category.setdefault(category, {"correct": 0, "total": 0})
            cat_stats["total"] += 1
            if outcome == "correct":
                cat_stats["correct"] += 1

            marker = "✓" if outcome == "correct" else ("?" if outcome == "unparseable" else "✗")
            if verbose or outcome != "correct":
                exp_str = f"expected={expected}"
                got_str = f"got={parsed!r}"
                raw_snippet = raw[:60].replace("\n", " ") if outcome != "correct" else ""
                print(f"  {marker} {name:<40} {exp_str:<25} {got_str}")
                if raw_snippet and outcome != "correct":
                    print(f"    raw: {raw_snippet}")
            else:
                print(f"  {marker} {name}")

            model_results.append({
                "case": name,
                "input": query,
                "expected": expected,
                "category": category,
                "parsed": parsed,
                "raw": raw[:200],
                "outcome": outcome,
            })

        total = correct + wrong + unparseable
        pct = int(100 * correct / total) if total else 0
        print(f"\n  Result: {correct}/{total} correct ({pct}%)")
        print(f"  By category:")
        for cat, stats in sorted(by_category.items()):
            c, t = stats["correct"], stats["total"]
            cp = int(100 * c / t) if t else 0
            print(f"    {cat:<15} {c}/{t} ({cp}%)")

        all_results[model_name] = {
            "size_gb": size_gb,
            "type": model_type,
            "correct": correct,
            "wrong": wrong,
            "unparseable": unparseable,
            "total": total,
            "pct": pct,
            "by_category": by_category,
            "cases": model_results,
        }

    return all_results


# ── Summary table ─────────────────────────────────────────────────────────────

def print_summary(all_results: dict) -> None:
    """Print cross-model comparison table sorted by score descending."""
    print(f"\n{'='*65}")
    print("  CROSS-MODEL SUMMARY")
    print(f"{'='*65}")
    print(f"  {'Model':<35} {'Size':>6} {'Type':>7}  {'Score':>10}  {'Pos':>5}  {'Par':>5}  {'Neg':>5}")
    print(f"  {'─'*35} {'─'*6} {'─'*7}  {'─'*10}  {'─'*5}  {'─'*5}  {'─'*5}")

    rows = []
    for model_name, r in all_results.items():
        pos = r["by_category"].get("positive", {})
        par = r["by_category"].get("paraphrase", {})
        neg = r["by_category"].get("negative", {})
        pos_pct = int(100 * pos.get("correct", 0) / pos["total"]) if pos.get("total") else 0
        par_pct = int(100 * par.get("correct", 0) / par["total"]) if par.get("total") else 0
        neg_pct = int(100 * neg.get("correct", 0) / neg["total"]) if neg.get("total") else 0
        rows.append((model_name, r["size_gb"], r["type"], r["pct"],
                     pos_pct, par_pct, neg_pct, r["correct"], r["total"]))

    rows.sort(key=lambda x: -x[3])  # sort by overall % descending
    for model_name, size, mtype, pct, pos, par, neg, c, t in rows:
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {model_name:<35} {size:>5.1f}G {mtype:>7}  {c:>3}/{t:<3} {pct:>3}%  {pos:>4}%  {par:>4}%  {neg:>4}%")
    print(f"{'='*65}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Skill routing eval for Ollama models"
    )
    parser.add_argument(
        "--models", nargs="+",
        help="Specific model names to test (default: all installed)"
    )
    parser.add_argument(
        "--cases", type=pathlib.Path, default=DEFAULT_CASES,
        help=f"Path to YAML test cases (default: {DEFAULT_CASES})"
    )
    parser.add_argument(
        "--category", choices=["positive", "paraphrase", "negative"],
        help="Only run cases from this category"
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Skip models larger than 5GB"
    )
    parser.add_argument(
        "--json", type=pathlib.Path, metavar="FILE",
        help="Save full results to a JSON file"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show all cases including correct ones"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show the prompt without calling the API"
    )
    args = parser.parse_args()

    # Load skills
    skills = load_skill_metadata(SKILLS_DIR)
    if not skills:
        print(f"ERROR: No skills found in {SKILLS_DIR}", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(skills)} skills from {SKILLS_DIR}")

    # Load cases
    if not args.cases.exists():
        print(f"ERROR: Cases file not found: {args.cases}", file=sys.stderr)
        sys.exit(1)
    all_cases = parse_yaml_cases(args.cases)
    if args.category:
        all_cases = [c for c in all_cases if c.get("category") == args.category]
    print(f"Loaded {len(all_cases)} test cases")

    # Select models
    if args.models:
        # User-specified — preserve order, look up size/type from our table
        name_map = {m[0]: m for m in MODELS_ORDERED}
        selected = []
        for name in args.models:
            entry = name_map.get(name, (name, 0.0, "unknown"))
            selected.append(entry)
    else:
        selected = MODELS_ORDERED
        if args.fast:
            selected = [m for m in selected if m[1] <= 5.0]

    # Check Ollama is reachable
    if not args.dry_run:
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                installed_data = json.loads(resp.read())
            installed_names = {m["name"] for m in installed_data.get("models", [])}
        except Exception:
            print("ERROR: Cannot reach Ollama at http://localhost:11434", file=sys.stderr)
            print("Start it with: ollama serve", file=sys.stderr)
            sys.exit(1)

        # Filter to only installed models
        available = [m for m in selected if m[0] in installed_names]
        skipped = [m[0] for m in selected if m[0] not in installed_names]
        if skipped:
            print(f"Skipping {len(skipped)} models not installed: {skipped}")
        selected = available

    if not selected:
        print("No models to evaluate.")
        sys.exit(0)

    print(f"\nWill evaluate {len(selected)} model(s):")
    for name, size, mtype in selected:
        print(f"  {name} ({size:.1f}GB, {mtype})")

    # Run
    start_time = datetime.now()
    print(f"\nStarted: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = run_eval(
        selected, all_cases, skills,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    if not args.dry_run and all_results:
        print_summary(all_results)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"Total time: {elapsed:.0f}s")

        if args.json:
            args.json.write_text(
                json.dumps({
                    "timestamp": start_time.isoformat(),
                    "models": all_results,
                }, indent=2),
                encoding="utf-8",
            )
            print(f"Results saved to {args.json}")


if __name__ == "__main__":
    main()
