#!/usr/bin/env python3
"""
Verify all mandatory gates have corresponding tests.
"""
import sys
import os
from pathlib import Path

# Keywords that indicate a mandatory gate
GATE_KEYWORDS = ["MANDATORY", "MUST", "BLOCKER", "🔒"]

def scan_sop_gates(docs_dir):
    """Scan SOP documentation for mandatory gates."""
    gates = []
    docs_path = Path(docs_dir).expanduser()
    if not docs_path.exists():
        return gates
        
    for md_file in docs_path.rglob("*.md"):
        content = md_file.read_text()
        lines = content.splitlines()
        for i, line in enumerate(lines):
            for kw in GATE_KEYWORDS:
                if kw in line:
                    gates.append({
                        "file": str(md_file.relative_to(docs_path.parent if ".agent" in str(md_file) else docs_path)),
                        "line": i + 1,
                        "content": line.strip(),
                        "keyword": kw
                    })
                    break # Only one keyword per line needed
    return gates

def find_test_files(tests_dir):
    """Find all gatekeeper test files."""
    test_files = []
    tests_path = Path(tests_dir).expanduser()
    if not tests_path.exists():
        return test_files
        
    for py_file in tests_path.rglob("test_sop_gate_*.py"):
        test_files.append(py_file.stem)
    return test_files

def main():
    docs_dir = os.path.expanduser("~/.agent/docs")
    tests_dir = "tests/gatekeeper"
    
    gates = scan_sop_gates(docs_dir)
    test_files = find_test_files(tests_dir)
    
    if not gates:
        print("No mandatory gates found in SOP documentation.")
        sys.exit(0)
        
    print(f"📊 SOP Gate Test Coverage Report")
    print("=" * 32)
    
    covered_gates = []
    missing_tests = []
    
    for gate in gates:
        # Simple matching: filename stem in test file name (case-insensitive)
        stem = Path(gate["file"]).stem.lower().replace("-", "_")
        expected_test = f"test_sop_gate_{stem}"
        
        # Also lowercase the test files list for matching
        if expected_test in [t.lower() for t in test_files]:
            covered_gates.append(gate)
        else:
            missing_tests.append(gate)
            
    total = len(gates)
    covered = len(covered_gates)
    coverage = (covered / total) * 100 if total > 0 else 0
    
    print(f"Total Mandatory Gates: {total}")
    print(f"Gates With Tests:      {covered}")
    print(f"Coverage:              {coverage:.1f}%")
    print()
    
    if missing_tests:
        print("❌ Missing Tests:")
        # Group by file to reduce output
        by_file = {}
        for gate in missing_tests:
            by_file.setdefault(gate["file"], []).append(gate["line"])
            
        for file, lines in by_file.items():
            print(f"  - {file} (Lines: {', '.join(map(str, lines))})")
    else:
        print("✅ 100% Coverage! All mandatory gates have corresponding tests.")

if __name__ == "__main__":
    main()
