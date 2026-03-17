"""
Full 67-case eval against a single model. Saves results to the evals directory.
Usage: python3 run_eval.py [model_name]  (default: llama3.2:3b)
"""
import sys, json, time, pathlib, importlib

sys.path.insert(0, '/Users/marchansen/.gemini/antigravity/skills/evals')
import trigger_eval; importlib.reload(trigger_eval)
from trigger_eval import (
    load_skill_metadata, parse_yaml_cases, build_system_prompt,
    call_ollama, parse_response, score_result, SKILLS_DIR, DEFAULT_CASES,
)

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:3b"
safe_name = MODEL.replace(':', '_').replace('/', '_')

skills        = load_skill_metadata(SKILLS_DIR)
cases         = parse_yaml_cases(DEFAULT_CASES)
system_prompt = build_system_prompt(skills)
valid_names   = {n.lower() for n, _ in skills} | {"none"}

print(f"Model : {MODEL}")
print(f"Skills: {len(skills)}  Cases: {len(cases)}\n")
print(f"{'─'*72}")

correct = wrong = unparseable = 0
by_cat  = {}
rows    = []

for case in cases:
    t0       = time.time()
    raw      = call_ollama(MODEL, system_prompt, case["input"])
    elapsed  = round(time.time() - t0, 1)
    expected = case["expected"].lower()
    category = case.get("category", "positive")
    parsed   = parse_response(raw, valid_names)
    outcome  = score_result(parsed, expected)

    if   outcome == "correct":     correct     += 1
    elif outcome == "wrong":       wrong       += 1
    else:                          unparseable += 1

    cat = by_cat.setdefault(category, {"correct": 0, "total": 0})
    cat["total"] += 1
    if outcome == "correct":
        cat["correct"] += 1

    m = "✓" if outcome == "correct" else ("?" if outcome == "unparseable" else "✗")
    print(f"  {m} {case['name']:<42} {expected:<24} {parsed}")
    if outcome != "correct":
        print(f"      raw → {raw.strip()[:70]!r}")

    rows.append({
        "case": case["name"], "input": case["input"],
        "expected": expected, "category": category,
        "parsed": parsed, "raw": raw[:300], "outcome": outcome,
    })

total = correct + wrong + unparseable
pct   = int(100 * correct / total) if total else 0

print(f"\n{'═'*72}")
print(f"  Score: {correct}/{total} ({pct}%)   wrong={wrong}  unparseable={unparseable}")
for cat in ("positive", "paraphrase", "negative"):
    s = by_cat.get(cat, {"correct": 0, "total": 0})
    c, t = s["correct"], s["total"]
    p = int(100 * c / t) if t else 0
    bar = "█" * (p // 5)
    print(f"  {cat:<15} {c:>3}/{t:<3} ({p:>3}%)  {bar}")
print(f"{'═'*72}")

out = pathlib.Path(f'/Users/marchansen/.gemini/antigravity/skills/evals/results_{safe_name}.json')
out.write_text(json.dumps({
    "model": MODEL, "correct": correct, "wrong": wrong,
    "unparseable": unparseable, "total": total, "pct": pct,
    "by_category": by_cat, "cases": rows,
}, indent=2))
print(f"\nSaved → {out}")
