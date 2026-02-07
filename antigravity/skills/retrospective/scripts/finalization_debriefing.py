#!/usr/bin/env python3
"""
Finalization Debriefing Script

Generates post-finalization strategic analysis after Finalization completion.
Synthesizes mission results, reflection learnings, and provides
improvement suggestions for SOP and workflow optimization.

Usage:
    python finalization_debriefing.py [--session-id SESSION_ID] [--output-dir DIR]
"""

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_activity_summary() -> dict:
    """Get summary of git activity from the session."""
    activity = {
        "commits": [],
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0,
    }

    try:
        # Get recent commits (last 10)
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", "10", "--since=12 hours ago"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            activity["commits"] = [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip()
            ]

        # Get diff stats
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines and "changed" in lines[-1]:
                # Parse: "X files changed, Y insertions(+), Z deletions(-)"
                stat_line = lines[-1]
                parts = stat_line.split(",")
                for part in parts:
                    part = part.strip()
                    if "file" in part:
                        activity["files_changed"] = int(part.split()[0])
                    elif "insertion" in part:
                        activity["insertions"] = int(part.split()[0])
                    elif "deletion" in part:
                        activity["deletions"] = int(part.split()[0])
    except Exception:
        pass

    return activity


def load_reflection_data(project_dir: Path) -> list:
    """Load reflection data from recent sessions."""
    reflections = []

    # Check common reflection file locations
    reflection_paths = [
        project_dir / ".agent" / "reflections.json",
        project_dir / "reflections.json",
    ]

    for path in reflection_paths:
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Get last 5 reflections
                        reflections.extend(data[-5:])
                    elif isinstance(data, dict):
                        reflections.append(data)
            except Exception:
                pass

    return reflections


def analyze_handoff_quality(reflections: list, project_dir: Path) -> dict:
    """Analyze hand-off quality for multi-phase implementations."""
    handoff_analysis = {
        "was_multi_phase": False,
        "handoff_completed": False,
        "compliance_score": 0,
        "quality_assessment": "No multi-phase implementation detected",
        "issues_identified": [],
        "successor_readiness": "N/A",
        "process_efficiency": [],
    }

    # Check reflections for hand-off data
    for reflection in reflections:
        if isinstance(reflection, dict) and "handoff_quality" in reflection:
            handoff_data = reflection["handoff_quality"]
            if isinstance(handoff_data, dict):
                handoff_analysis["was_multi_phase"] = True

                # Extract hand-off quality metrics
                if handoff_data.get("was_multi_phase", False):
                    if handoff_data.get("handoff_completed", False):
                        handoff_analysis["handoff_completed"] = True
                        handoff_analysis["compliance_score"] = handoff_data.get(
                            "compliance_score", 0
                        )
                        handoff_analysis["quality_assessment"] = handoff_data.get(
                            "document_quality", "Unknown"
                        )
                        handoff_analysis["issues_identified"] = handoff_data.get(
                            "issues_found", []
                        )
                    else:
                        handoff_analysis["quality_assessment"] = (
                            "Hand-off not completed"
                        )
                        handoff_analysis["issues_identified"].append(
                            "Hand-off procedure not completed"
                        )

    # Also check hand-off directory directly
    handoff_dir = project_dir / ".agent" / "handoffs"
    if handoff_dir.exists():
        handoff_files = list(handoff_dir.glob("**/phase-*-handoff.md"))
        if handoff_files:
            handoff_analysis["was_multi_phase"] = True

            # Run verification script if available
            verification_script = (
                project_dir / ".agent" / "scripts" / "verify_handoff_compliance.sh"
            )
            if verification_script.exists():
                try:
                    result = subprocess.run(
                        [str(verification_script), "--report"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=project_dir,
                    )

                    if result.returncode == 0:
                        handoff_analysis["handoff_completed"] = True
                        # Parse compliance score
                        for line in result.stdout.split("\n"):
                            if "Compliance:" in line:
                                try:
                                    score_str = (
                                        line.split("Compliance:")[1].strip().rstrip("%")
                                    )
                                    handoff_analysis["compliance_score"] = int(
                                        score_str
                                    )
                                except:
                                    pass
                        handoff_analysis["quality_assessment"] = (
                            "Automated verification passed"
                        )
                    else:
                        handoff_analysis["quality_assessment"] = (
                            "Automated verification failed"
                        )
                        handoff_analysis["issues_identified"].append(
                            result.stderr.strip()
                        )
                except Exception as e:
                    handoff_analysis["quality_assessment"] = (
                        f"Verification error: {str(e)}"
                    )
                    handoff_analysis["issues_identified"].append(
                        f"Could not run verification: {str(e)}"
                    )
            else:
                handoff_analysis["issues_identified"].append(
                    "Verification script not found"
                )

    # Generate process efficiency insights
    if handoff_analysis["was_multi_phase"]:
        if handoff_analysis["handoff_completed"]:
            if handoff_analysis["compliance_score"] >= 95:
                handoff_analysis["process_efficiency"].append(
                    "Excellent hand-off quality (>95% compliance)"
                )
            elif handoff_analysis["compliance_score"] >= 80:
                handoff_analysis["process_efficiency"].append(
                    "Good hand-off quality (>80% compliance)"
                )
            else:
                handoff_analysis["process_efficiency"].append(
                    "Hand-off quality needs improvement (<80% compliance)"
                )
        else:
            handoff_analysis["process_efficiency"].append(
                "Hand-off process incomplete - blocks phase transitions"
            )

    return handoff_analysis


def analyze_friction_patterns(reflections: list) -> list:
    """Analyze reflections for friction patterns."""
    friction_items = []

    for reflection in reflections:
        if isinstance(reflection, dict):
            # Check for challenges
            challenges = reflection.get("challenges_overcome", [])
            if isinstance(challenges, list):
                friction_items.extend(challenges)

            # Check for process issues
            process_issues = reflection.get("process_improvements", [])
            if isinstance(process_issues, list):
                friction_items.extend(process_issues)

    return list(set(friction_items))[:10]  # Deduplicate and limit


def generate_improvement_suggestions(
    git_activity: dict, reflections: list, friction: list
) -> dict:
    """Generate improvement suggestions based on session data."""
    suggestions = {
        "friction_reduction": [],
        "efficiency_improvements": [],
        "agentic_patterns": [],
        "cognitive_load_reduction": [],
        "design_patterns": [],
    }

    # Friction reduction based on activity patterns
    if git_activity.get("commits", []):
        commit_count = len(git_activity["commits"])
        if commit_count > 5:
            suggestions["friction_reduction"].append(
                "High commit frequency detected. Consider batching related changes."
            )

    if friction:
        suggestions["friction_reduction"].extend(
            [f"Address friction point: {item}" for item in friction[:3]]
        )

    # Efficiency improvements
    if git_activity.get("files_changed", 0) > 20:
        suggestions["efficiency_improvements"].append(
            "Large number of files changed. Consider breaking into smaller, focused changes."
        )

    # Agentic design patterns - always include these prompts
    suggestions["agentic_patterns"] = [
        "Consider: Could any part of this work be parallelized across agents?",
        "Review: Are there clear handoff points that could improve multi-agent workflows?",
        "Evaluate: Would task decomposition benefit from explicit dependency declarations?",
    ]

    # Cognitive load reduction analysis
    suggestions["cognitive_load_reduction"] = [
        "QUESTION: Are there parts of the SOP where the agent's cognitive load "
        "could be reduced by using scripts?",
        "Review manual steps in Initialization/Finalization that could be automated",
        "Identify repeated decision points that could have default behaviors",
    ]

    # Design patterns and refactoring
    suggestions["design_patterns"] = [
        "QUESTION: Identify design patterns and recommended refactoring strategies.",
        "Consider: Are there emerging patterns that should be formalized as skills?",
        "Evaluate: Would template-based approaches reduce boilerplate work?",
    ]

    return suggestions


def generate_debrief(
    session_id: str,
    output_dir: Path,
    project_dir: Path | None = None,
) -> str:
    """Generate the mission debrief document."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Gather data
    if project_dir is None:
        project_dir = Path.cwd()

    git_activity = get_git_activity_summary()
    reflections = load_reflection_data(project_dir)
    friction = analyze_friction_patterns(reflections)
    handoff_quality = analyze_handoff_quality(reflections, project_dir)
    suggestions = generate_improvement_suggestions(git_activity, reflections, friction)

    # Build debrief markdown
    debrief_lines = [
        "# Finalization Debriefing",
        "",
        f"**Session**: {session_id}",
        f"**Timestamp**: {timestamp}",
        "",
        "---",
        "",
        "## 1. Mission Summary",
        "",
    ]

    # Git activity summary
    if git_activity["commits"]:
        debrief_lines.extend(
            [
                "### Git Activity",
                f"- **Commits**: {len(git_activity['commits'])}",
                f"- **Files Changed**: {git_activity['files_changed']}",
                f"- **Lines Added**: {git_activity['insertions']}",
                f"- **Lines Removed**: {git_activity['deletions']}",
                "",
                "**Recent Commits**:",
            ]
        )
        for commit in git_activity["commits"][:5]:
            debrief_lines.append(f"- `{commit}`")
        debrief_lines.append("")
    else:
        debrief_lines.extend(
            [
                "No git activity detected in this session.",
                "",
            ]
        )

    # Hand-off quality assessment
    debrief_lines.extend(
        [
            "---",
            "",
            "## 2. Multi-Phase Implementation Assessment",
            "",
        ]
    )

    if handoff_quality["was_multi_phase"]:
        debrief_lines.extend(
            [
                f"**Implementation Type**: Multi-phase detected",
                f"**Hand-off Completed**: {'✅ Yes' if handoff_quality['handoff_completed'] else '❌ No'}",
                f"**Compliance Score**: {handoff_quality['compliance_score']}%",
                f"**Quality Assessment**: {handoff_quality['quality_assessment']}",
                "",
            ]
        )

        if handoff_quality["process_efficiency"]:
            debrief_lines.append("### Process Efficiency Insights")
            for insight in handoff_quality["process_efficiency"]:
                debrief_lines.append(f"- {insight}")
            debrief_lines.append("")

        if handoff_quality["issues_identified"]:
            debrief_lines.append("### Issues Identified")
            for issue in handoff_quality["issues_identified"]:
                debrief_lines.append(f"- {issue}")
            debrief_lines.append("")

        # Successor readiness assessment
        debrief_lines.extend(
            [
                "### Successor Agent Readiness",
                f"**Readiness Level**: {handoff_quality['successor_readiness']}",
                "",
            ]
        )
    else:
        debrief_lines.extend(
            [
                "**Implementation Type**: Single-phase implementation",
                "**Hand-off Assessment**: Not applicable",
                "",
            ]
        )

    # Reflection synthesis
    debrief_lines.extend(
        [
            "---",
            "",
            "## 3. Reflection Synthesis",
            "",
        ]
    )

    if reflections:
        # Extract key learnings
        all_learnings = []
        for r in reflections:
            if isinstance(r, dict):
                learnings = r.get("technical_learnings", [])
                if isinstance(learnings, list):
                    all_learnings.extend(learnings)

        if all_learnings:
            debrief_lines.append("### Key Learnings")
            for learning in all_learnings[:5]:
                debrief_lines.append(f"- {learning}")
            debrief_lines.append("")

        if friction:
            debrief_lines.append("### Friction Points Identified")
            for item in friction[:5]:
                debrief_lines.append(f"- {item}")
            debrief_lines.append("")
    else:
        debrief_lines.extend(
            [
                "No reflection data available from this session.",
                "",
            ]
        )

    # Improvement suggestions
    debrief_lines.extend(
        [
            "---",
            "",
            "## 4. Improvement Suggestions",
            "",
        ]
    )

    if suggestions["friction_reduction"]:
        debrief_lines.append("### 🔧 Friction Reduction")
        for item in suggestions["friction_reduction"]:
            debrief_lines.append(f"- {item}")
        debrief_lines.append("")

    if suggestions["efficiency_improvements"]:
        debrief_lines.append("### ⚡ Efficiency Improvements")
        for item in suggestions["efficiency_improvements"]:
            debrief_lines.append(f"- {item}")
        debrief_lines.append("")

    debrief_lines.append("### 🤖 Agentic Design Patterns")
    for item in suggestions["agentic_patterns"]:
        debrief_lines.append(f"- {item}")
    debrief_lines.append("")

    # Strategic questions section
    debrief_lines.extend(
        [
            "---",
            "",
            "## 5. Strategic Analysis Questions",
            "",
            "### Cognitive Load Reduction",
        ]
    )
    for item in suggestions["cognitive_load_reduction"]:
        debrief_lines.append(f"- {item}")
    debrief_lines.append("")

    debrief_lines.append("### Design Patterns & Refactoring")
    for item in suggestions["design_patterns"]:
        debrief_lines.append(f"- {item}")
    debrief_lines.append("")

    # Harness Self-Evolution (P0: SOTA Harness Migration)
    debrief_lines.extend(
        [
            "---",
            "",
            "## 6. Harness Self-Evolution (MANDATORY)",
            "",
            "### RBT Analysis",
            "- **Roses** (Successes): IDENTIFY what part of the harness/SOP worked perfectly.",
            "- **Buds** (Potential): IDENTIFY an emerging improvement for the next session.",
            "- **Thorns** (Challenges): IDENTIFY one failure point in the protocol today.",
            "",
            "### Protocol Validity",
            "- [ ] Orchestrator was accurate in its checks",
            "- [ ] `task.md` remained the living source of truth",
            "- [ ] `SKILL.md` updates were proposed for new learnings",
            "",
            "### Memory Sync",
            "- [ ] All session learnings synced to AutoMem Knowledge Graph",
            "- [ ] OpenViking temporal state persisted",
            "",
        ]
    )

    # Footer
    debrief_lines.extend(
        [
            "---",
            "",
            "*Generated by Finalization Debriefing Skill*",
            f"*{timestamp}*",
        ]
    )

    debrief_content = "\n".join(debrief_lines)

    # Save to file
    output_file = output_dir / "debrief.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(debrief_content)

    return debrief_content


def main():
    parser = argparse.ArgumentParser(
        description="Generate finalization debriefing after Finalization completion"
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Session identifier (defaults to timestamp)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for debrief file",
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Project directory to analyze",
    )

    args = parser.parse_args()

    # Determine session ID
    session_id = args.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Default to brain directory with session ID
        brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
        output_dir = brain_dir / session_id

    # Determine project directory
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()

    print("🎖️  Finalization Debriefing")
    print("=" * 40)
    print()

    # Generate and print debrief
    debrief = generate_debrief(session_id, output_dir, project_dir)
    print(debrief)

    print()
    print("=" * 40)
    print(f"✅ Debrief saved to: {output_dir / 'debrief.md'}")


if __name__ == "__main__":
    main()
