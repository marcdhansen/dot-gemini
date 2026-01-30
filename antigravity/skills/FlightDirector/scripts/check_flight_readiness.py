import argparse
import subprocess
import sys
import os
import glob
import shutil
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return stdout+stderr. Raises error on failure."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            cwd=cwd,
        )
        return result.stdout.strip(), result.returncode
    except Exception:
        return None, 1


def check_pfc():
    """Pre-Flight Check: Verify Beads issue and Task artifact."""
    print("🛫 Initiating Pre-Flight Check (PFC)...")
    errors = []

    # 1. Check Beads
    bd_check, code = run_command("bd ready")
    if bd_check is None or code != 0:
        errors.append(
            "❌ Beads (`bd`) check failed. Is beads installed and initialized?"
        )
    else:
        print("✅ Beads System: ONLINE")

    # 2. Check Task Artifacts
    cwd = Path.cwd()
    task_file = cwd / "task.md"
    if not task_file.exists():
        errors.append("❌ `task.md` missing in current directory.")
    else:
        print("✅ `task.md`: FOUND")

    rules_dir = cwd / ".agent" / "rules"
    if not rules_dir.exists():
        errors.append(
            "❌ `.agent/rules/` directory missing. Planning documents required."
        )
    else:
        roadmap = rules_dir / "ROADMAP.md"
        plan = rules_dir / "ImplementationPlan.md"
        if not roadmap.exists():
            errors.append("❌ `ROADMAP.md` missing in .agent/rules/")
        if not plan.exists():
            errors.append("❌ `ImplementationPlan.md` missing in .agent/rules/")
        if roadmap.exists() and plan.exists():
            print("✅ Planning Documents: FOUND")

    if errors:
        print("\n🛑 PFC FAILED:")
        for e in errors:
            print(f"   {e}")
        sys.exit(1)
    else:
        print("\n✅ PFC PASSED. You are clear for takeoff.")


def get_temp_artifacts():
    """Returns a list of matching temporary artifacts."""
    temp_patterns = [
        "rag_storage_*",
        "test_output.txt",
        "debug_*.py",
        "testing_server_autostart.log",
        "temp",
        "test_ace_curator*",
        "tests/rag_storage_*",
    ]
    found = []
    for pattern in temp_patterns:
        matches = glob.glob(pattern)
        found.extend(matches)
    return found


def get_bloat_patterns(base_dir):
    """Returns aggressive bloat patterns for given directory."""
    patterns = [
        # Large binary files
        "**/*.log",
        "**/*.cache",
        "**/cache/**",
        "**/tmp/**",
        "**/temp/**",
        "**/__pycache__/**",
        "*.pyc",
        "*.pyo",
        # Browser profiles and large data
        "**/.mozilla/**",
        "**/.chrome/**",
        "**/.google-chrome/**",
        "**/chromium/**",
        # Build artifacts
        "**/node_modules/**",
        "**/build/**",
        "**/dist/**",
        "**/target/**",
        "**/venv/**",
        "**/env/**",
        "**/.venv/**",
        # Large temporary files (>10MB)
        "**/*.tmp",
        "**/*.temp",
        "**/*.bak",
        "**/*.old",
        "**/*.swp",
        "**/.DS_Store",
        # Package manager caches
        "**/pip-cache/**",
        "**/uv-cache/**",
        "**/npm-cache/**",
        "**/.cargo/registry/cache/**",
    ]

    found = []
    for pattern in patterns:
        matches = glob.glob(os.path.join(base_dir, pattern), recursive=True)
        found.extend(matches)

    # Also find large files (>10MB) that aren't in git
    try:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # >10MB
                        found.append(file_path)
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass

    return found


def clean_bloat_aggressively():
    """Aggressively clean bloat from global config directories."""
    print("🔥 Performing aggressive bloat removal...")

    global_dirs = [
        os.path.expanduser("~/.gemini"),
        os.path.expanduser("~/.antigravity"),
    ]

    total_removed = 0
    total_size_saved = 0

    for base_dir in global_dirs:
        if not os.path.exists(base_dir):
            continue

        print(f"   🧹 Scanning {base_dir}...")
        bloat_items = get_bloat_patterns(base_dir)

        if not bloat_items:
            print(f"   ✅ No bloat found in {base_dir}")
            continue

        for item in bloat_items:
            try:
                path = Path(item)
                size_before = 0

                if path.exists():
                    if path.is_file():
                        size_before = path.stat().st_size
                        path.unlink()
                    elif path.is_dir():
                        # Calculate directory size
                        for root, dirs, files in os.walk(item):
                            for file in files:
                                try:
                                    size_before += os.path.getsize(
                                        os.path.join(root, file)
                                    )
                                except (OSError, PermissionError):
                                    continue
                        shutil.rmtree(path)

                    total_removed += 1
                    total_size_saved += size_before
                    print(f"   🗑️  Removed: {item} ({size_before / 1024 / 1024:.1f}MB)")

            except (OSError, PermissionError) as e:
                print(f"   ❌ Failed to remove {item}: {e}")

    print(
        f"   ✅ Bloat removal complete: {total_removed} items, {total_size_saved / 1024 / 1024:.1f}MB freed"
    )
    return total_removed, total_size_saved


def clean_artifacts():
    """Purges detected temporary artifacts."""
    artifacts = get_temp_artifacts()
    if not artifacts:
        print("✅ No temporary artifacts found to clean.")
        return

    print("🧹 Cleaning temporary artifacts...")
    for art in artifacts:
        path = Path(art)
        try:
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Deleted directory: {art}")
            else:
                path.unlink()
                print(f"   Deleted file: {art}")
        except Exception as e:
            print(f"   ❌ Failed to delete {art}: {e}")


def check_rtb():
    """Return To Base: Verify Git, Beads, and Cleanup."""
    print("🛬 Initiating Return To Base (RTB) Check...")
    warnings = []
    critical_errors = []

    # 0. Aggressive Bloat Removal (Always executed)
    print("🔥 Aggressive Bloat Removal Phase...")
    removed_items, size_saved = clean_bloat_aggressively()
    if removed_items == 0:
        print("✅ Aggressive Bloat Removal: NO BLOAT FOUND")
    else:
        print(
            f"✅ Aggressive Bloat Removal: CLEANED {removed_items} items ({size_saved / 1024 / 1024:.1f}MB)"
        )

    # 1. Git Status
    git_status, code = run_command("git status --porcelain")
    if git_status is None:
        critical_errors.append("❌ Git Status Check FAILED. Is this a git repo?")
    elif git_status.strip():
        warnings.append(f"⚠️ Git Repository has uncommitted changes:\n{git_status}")
    else:
        print("✅ Git Repository: CLEAN")

    # 2. Cleanup Check
    found_temp = get_temp_artifacts()
    if found_temp:
        warnings.append(
            f"⚠️ Temporary artifacts found (Run with --clean to purge):\n   {', '.join(found_temp)}"
        )
    else:
        print("✅ Cleanup: NO TEMPORARY ARTIFACTS FOUND")

    # 3. Markdown Lint
    mdlint_path, code = run_command("which markdownlint")
    if mdlint_path:
        # Check task.md and .agent/rules/
        lint_cmd = "markdownlint task.md .agent/rules/*.md"
        lint_out, lint_code = run_command(lint_cmd)
        if lint_code != 0:
            # Filter MD013 if needed, or just report
            warnings.append(f"⚠️ Markdown Lint issues found:\n{lint_out}")
        else:
            print("✅ Markdown Lint: PASSED")
    else:
        print("ℹ️ markdownlint not found. Skipping lint check.")

    # 4. Code Quality (pre-commit)
    print("📋 Checking code quality (pre-commit)...")
    pc_out, pc_code = run_command("pre-commit run --all-files")
    if pc_code != 0:
        # Pre-commit failed. We should provide a summary.
        warnings.append(
            f"⚠️ Pre-commit checks failed! Please fix linting/formatting:\n{pc_out}"
        )
    else:
        print("✅ Pre-commit checks: PASSED")

    # 4.5 Documentation Coverage
    doc_check_script = Path("scripts/check_docs_coverage.py")
    if doc_check_script.exists():
        print("📋 Checking documentation coverage & portability...")
        doc_out, doc_code = run_command("python3 scripts/check_docs_coverage.py")
        if doc_code != 0:
            warnings.append(f"⚠️ Documentation coverage issues found:\n{doc_out}")
        else:
            print("✅ Documentation Coverage: PASSED")

    # 5. WebUI Lint Check
    webui_dir = Path("lightrag_webui")
    if webui_dir.exists():
        print("📋 Checking WebUI code quality...")
        lint_out, lint_code = run_command("cd lightrag_webui && bun run lint")
        if lint_code != 0:
            warnings.append(f"⚠️ WebUI Lint Checks failed!\n{lint_out}")
        else:
            print("✅ WebUI Lint: PASSED")

    # 5. Beads Status
    bd_list, code = run_command("bd list --limit 5")
    if code == 0 and bd_list:
        print(f"ℹ️ Recent Tasks:\n{bd_list}")
        print(
            "   (Did you close your task? Did you list NEW issues created in your Handoff?)"
        )

    if critical_errors:
        print("\n🛑 RTB FAILED (CRITICAL):")
        for e in critical_errors:
            print(f"   {e}")
        sys.exit(1)
    elif warnings:
        print("\n⚠️ RTB WARNINGS (Please address before final handoff):")
        for w in warnings:
            print(f"   {w}")
        sys.exit(1)
    else:
        print("\n✅ RTB PASSED. Ready for handoff.")


def main():
    parser = argparse.ArgumentParser(description="Flight Director: SMP Enforcement")
    parser.add_argument("--pfc", action="store_true", help="Run Pre-Flight Check")
    parser.add_argument("--rtb", action="store_true", help="Run Return To Base Check")
    parser.add_argument(
        "--clean", action="store_true", help="Purge temporary artifacts"
    )
    parser.add_argument(
        "--clean-bloat",
        action="store_true",
        help="Perform aggressive bloat removal from global config directories",
    )

    args = parser.parse_args()

    if args.clean:
        clean_artifacts()

    if args.clean_bloat:
        clean_bloat_aggressively()

    if args.pfc:
        check_pfc()
    elif args.rtb:
        check_rtb()
    elif not args.clean and not args.clean_bloat:
        parser.print_help()


if __name__ == "__main__":
    main()
