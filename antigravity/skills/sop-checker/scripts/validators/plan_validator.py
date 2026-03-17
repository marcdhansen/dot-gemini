import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta
from .common import check_tool_available


def check_planning_docs(*args) -> tuple[bool, list[str]]:
    """Check if planning documents exist and are readable. Supports checklist args."""
    project_root = Path.cwd()
    roadmap_locations = [
        project_root / ".agent/rules/ROADMAP.md",
        project_root / ".agent/ROADMAP.md",
        project_root / "ROADMAP.md",
    ]
    impl_locations = [
        project_root / ".agent/rules/ImplementationPlan.md",
        project_root / ".agent/ImplementationPlan.md",
        project_root / "ImplementationPlan.md",
    ]

    roadmap_exists = any(p.exists() for p in roadmap_locations)
    impl_exists = any(p.exists() for p in impl_locations)

    if args:
        if args[0] == "ImplementationPlan.md":
            if not impl_exists:
                return False, ["ImplementationPlan.md missing"]
            return True, ["ImplementationPlan.md exists"]
        if args[0] == "blast_radius":
            for p in impl_locations:
                if p.exists() and "Blast Radius" in p.read_text():
                    return True, ["Blast radius analysis found"]
            return False, ["Blast radius analysis not found in ImplementationPlan.md"]

    missing = []
    if not roadmap_exists:
        missing.append("ROADMAP.md")
    if not impl_exists:
        missing.append("ImplementationPlan.md")

    return len(missing) == 0, missing


def check_beads_issue(*args) -> tuple[bool, str]:
    """Check if there's an active beads issue and verify it's started on this branch for implementation.

    Args:
        *args: Optional arguments. If 'require_started' is passed, strictly enforces started state.
    """
    if not check_tool_available("bd"):
        return False, "beads (bd) not available"

    import json
    from .git_validator import get_active_issue_id, check_branch_info

    require_started = "require_started" in args
    branch, is_feature = check_branch_info()
    active_id = get_active_issue_id()

    # Strictly enforce started state on feature branches or if explicitly requested
    if is_feature or require_started:
        if not active_id:
            return (
                False,
                f"Could not identify active Beads issue from branch '{branch}'. Branch must follow 'agent/issue-id' pattern.",
            )

        try:
            result = subprocess.run(
                ["bd", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                issues = json.loads(result.stdout)
                for issue in issues:
                    if issue["id"] == active_id:
                        labels = issue.get("labels", [])
                        is_started = any(l in labels for l in ["status:started", "started:true"])
                        is_in_progress = issue.get("status") == "in_progress"

                        if is_started or is_in_progress:
                            return (
                                True,
                                f"Active issue {active_id} is {issue.get('status')} on branch '{branch}'",
                            )
                        else:
                            return (
                                False,
                                f"Issue {active_id} is found but NOT started. Run: bd set-state {active_id} started=true",
                            )
                return (
                    False,
                    f"Active issue {active_id} (derived from branch '{branch}') not found in Beads database",
                )
        except Exception as e:
            return False, f"Error verifying started state: {e}"

    # Fallback/Initial check for planning on non-feature branches
    try:
        result = subprocess.run(
            ["bd", "ready"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = [
                l for l in result.stdout.strip().split("\n") if l.strip() and "Ready work" not in l
            ]
            if lines:
                return True, f"Issues ready for planning: {len(lines)}"
        return False, "No active Beads issues found for planning"
    except Exception as e:
        return False, f"beads check failed: {e}"


def check_sop_simplification() -> tuple[bool, str]:
    """Check for SOP simplification proposals and their validation status."""
    proposal_patterns = [
        "*.md",
        ".agent/sop_simplification_*.md",
        "sop_simplification_*.md",
    ]

    proposals = []
    for pattern in proposal_patterns:
        proposals.extend(Path(".").glob(pattern))
        proposals.extend(Path(".agent").glob(pattern))

    if not proposals:
        return True, "No SOP simplification proposals found"

    pending_proposals = []
    approved_proposals = []

    for proposal in proposals:
        if "sop_simplification_" in proposal.name:
            content = proposal.read_text()
            if "## Approval Section" in content:
                if "Approve Simplified" in content:
                    approved_proposals.append(proposal.name)
                elif "Approve Standard" in content or "Reject" in content:
                    continue
                else:
                    pending_proposals.append(proposal.name)
            else:
                pending_proposals.append(proposal.name)

    if pending_proposals:
        return (
            False,
            f"Pending SOP simplification proposals: {', '.join(pending_proposals)}",
        )

    if approved_proposals:
        return True, f"Approved simplified SOP: {', '.join(approved_proposals)}"

    return True, "SOP simplification proposals processed"


def check_hook_integrity() -> tuple[bool, str]:
    """Check if git hooks are intact and not tampered with. Supports pre-commit and beads."""
    standard_hooks = {
        "pre-commit-framework": {
            ".git/hooks/pre-commit": [
                "#!/usr/bin/env bash",
                "# File generated by pre-commit:",
                'pre_commit "${ARGS[@]}"',
            ],
            ".git/hooks/pre-push": [
                "#!/usr/bin/env bash",
                "# File generated by pre-commit:",
                'pre_commit "${ARGS[@]}"',
            ],
        },
        "beads": {
            ".git/hooks/pre-commit": [
                "bd (beads) pre-commit hook",
                # Support both legacy and shim patterns
                ["bd sync --flush-only", "bd hooks run pre-commit"],
            ],
            ".git/hooks/post-merge": [
                "bd (beads) post-merge hook",
                ["bd import", "bd hooks run post-merge"],
            ],
        },
    }

    detected_standard = None
    if Path(".pre-commit-config.yaml").exists():
        detected_standard = "pre-commit-framework"
    elif Path(".beads").exists():
        detected_standard = "beads"

    if not detected_standard:
        for name, hook_set in standard_hooks.items():
            for path, patterns in hook_set.items():
                hook_file = Path(path)
                if hook_file.exists() and hook_file.is_file():
                    content = hook_file.read_text()
                    if all(pattern in content for pattern in patterns):
                        detected_standard = name
                        break
            if detected_standard:
                break

    if not detected_standard:
        return True, "No standard hook framework detected (Integrity check skipped)"

    hook_set = standard_hooks[detected_standard]
    missing_hooks = []
    tampered_hooks = []

    for hook_path, expected_patterns in hook_set.items():
        hook_file = Path(hook_path)
        if not hook_file.exists():
            missing_hooks.append(hook_path)
            continue

        if not hook_file.is_file() or not os.access(hook_file, os.X_OK):
            tampered_hooks.append(f"{hook_path} (not executable or not a file)")
            continue

        content = hook_file.read_text()
        for pattern in expected_patterns:
            if isinstance(pattern, list):
                if not any(p in content for p in pattern):
                    tampered_hooks.append(
                        f"{hook_path} (missing one of expected patterns: {', '.join([p[:20] for p in pattern])}...)"
                    )
                    break
            elif pattern not in content:
                tampered_hooks.append(f"{hook_path} (missing expected pattern: {pattern[:30]}...)")
                break

    if missing_hooks or tampered_hooks:
        issues = []
        if missing_hooks:
            issues.append(f"Missing hooks: {', '.join(missing_hooks)}")
        if tampered_hooks:
            issues.append(f"Tampered hooks: {', '.join(tampered_hooks)}")
        return False, f"Hook integrity failure ({detected_standard}): {'; '.join(issues)}"

    return True, f"All {detected_standard} hooks intact"


def get_approval_ttl() -> int:
    """Load approval TTL from orchestrator.yaml or return default (4h)."""
    config_path = Path.cwd() / "orchestrator.yaml"
    if not config_path.exists():
        return 4

    try:
        import yaml

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        return config.get("approval", {}).get("default_ttl_hours", 4)
    except Exception:
        return 4


def check_plan_approval(*args) -> tuple[bool, str]:
    """Check if plan approval exists and is fresh. Supports 'invert' argument."""
    max_hours = None
    invert = False

    if args:
        if args[0] == "invert":
            invert = True
        else:
            try:
                max_hours = int(args[0])
            except ValueError:
                pass

    if max_hours is None:
        max_hours = get_approval_ttl()

    task_paths = [
        Path(".agent/task.md"),
        Path("task.md"),
    ]

    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if brain_dir.exists():
        for session_dir in sorted(brain_dir.iterdir(), reverse=True)[:3]:
            if session_dir.is_dir():
                task_paths.append(session_dir / "task.md")

    for task_path in task_paths:
        if task_path.exists():
            try:
                content = task_path.read_text()
                if (
                    "## Approval" in content
                    and "[x]" in content[content.find("## Approval") :].lower()
                ):
                    if invert:
                        return False, "Plan approval marker still present in task.md"

                    mtime = datetime.fromtimestamp(task_path.stat().st_mtime)
                    age = datetime.now() - mtime

                    if age < timedelta(hours=max_hours):
                        hours_ago = age.total_seconds() / 3600
                        return True, f"Plan approved {hours_ago:.1f} hours ago"
                    else:
                        hours_ago = age.total_seconds() / 3600
                        return (
                            False,
                            f"Plan approval is {hours_ago:.1f} hours old (stale)",
                        )
            except Exception:
                pass

    if invert:
        return True, "Plan approval marker cleared"
    return False, "No plan approval found"


def check_api_documentation() -> tuple[bool, str]:
    """Check if API design docs exist in plan when feature involves API changes.

    BLOCKER: If there's an API change, documentation must exist.
    """
    project_root = Path.cwd()

    plan_locations = [
        project_root / ".agent/rules/ImplementationPlan.md",
        project_root / ".agent/ImplementationPlan.md",
        project_root / "ImplementationPlan.md",
    ]

    impl_plan_pattern = project_root / ".agent/plans" / "*.md"

    impl_plan_files = list(project_root.glob(".agent/plans/*.md"))

    api_section_found = False
    api_files_checked = []

    for plan_file in plan_locations + impl_plan_files:
        if plan_file.exists():
            try:
                content = plan_file.read_text()
                if "## API Design" in content:
                    api_section_found = True
                    api_files_checked.append(plan_file.name)
                elif "is_api_change: true" in content.lower():
                    api_section_found = True
                    api_files_checked.append(plan_file.name)
            except Exception:
                pass

    if api_section_found:
        return True, f"API documentation found in: {', '.join(api_files_checked)}"

    if not api_files_checked:
        plans_exist = [p.name for p in plan_locations if p.exists()]
        if plans_exist:
            return True, f"No API changes detected (checked: {', '.join(plans_exist[:2])})"
        return True, "No plan files found - skipping API documentation check"

    return False, "API changes detected but no API documentation found in plan"


def check_beads_issue_created() -> tuple[bool, str]:
    """Verify beads issue was created after plan approval.

    BLOCKER: Issue must exist for execution to proceed.
    """
    if not check_tool_available("bd"):
        return False, "beads (bd) not available"

    from .git_validator import get_active_issue_id, check_branch_info

    branch, is_feature = check_branch_info()
    active_id = get_active_issue_id()

    if not active_id:
        return (
            False,
            "Could not identify active Beads issue from branch. Run 'bd start <issue-id>' first.",
        )

    try:
        result = subprocess.run(
            ["bd", "show", active_id, "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            import json

            issue = json.loads(result.stdout)
            issue_type = issue.get("type", "unknown")
            return True, f"Beads issue {active_id} exists (type: {issue_type})"
        else:
            return (
                False,
                f"Beads issue {active_id} not found. Create it with 'bd create' or check the ID.",
            )
    except Exception as e:
        return False, f"Error verifying beads issue: {e}"


def check_plan_storage(*args) -> tuple[bool, str]:
    """Verify plan stored in .agent/plans/{issue-id}.md with bi-directional links.

    BLOCKER: Plan must be stored with issue ID for proper linkage.
    Auto-fix: Creates plan file from ImplementationPlan.md if missing.
    """
    from .git_validator import get_active_issue_id, check_branch_info

    project_root = Path.cwd()
    branch, is_feature = check_branch_info()
    active_id = get_active_issue_id()

    if not active_id:
        return False, "Could not identify active Beads issue from branch"

    plans_dir = project_root / ".agent" / "plans"
    plan_file = plans_dir / f"{active_id}.md"

    if plan_file.exists():
        content = plan_file.read_text()
        if active_id in content:
            return True, f"Plan stored at .agent/plans/{active_id}.md with issue linkage"
        return False, f"Plan file exists but missing issue ID reference"

    legacy_plans = [
        project_root / ".agent/rules/ImplementationPlan.md",
        project_root / ".agent/ImplementationPlan.md",
        project_root / "ImplementationPlan.md",
    ]

    legacy_plan = None
    for lp in legacy_plans:
        if lp.exists():
            legacy_plan = lp
            break

    if not legacy_plan:
        return False, f"No plan found. Create .agent/plans/{active_id}.md or ImplementationPlan.md"

    if "auto-fix" in args:
        try:
            plans_dir.mkdir(parents=True, exist_ok=True)
            content = legacy_plan.read_text()

            header = f"""# Implementation Plan: {active_id}

**Beads Issue**: {active_id}
**Status**: IN_PROGRESS
**Created**: {datetime.now().strftime("%Y-%m-%d")}
**Plan Link**: .agent/plans/{active_id}.md

---

"""
            new_content = header + content

            plan_file.write_text(new_content)
            return True, f"Auto-created .agent/plans/{active_id}.md from {legacy_plan.name}"
        except Exception as e:
            return False, f"Auto-fix failed: {e}"

    return (
        False,
        f"Plan not found at .agent/plans/{active_id}.md. Run with auto-fix to create from ImplementationPlan.md",
    )
