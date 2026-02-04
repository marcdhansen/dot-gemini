#!/usr/bin/env python3
"""
Mission Debriefing Script

Generates post-mission strategic analysis after RTB completion.
Synthesizes mission results, reflection learnings, and provides
improvement suggestions for SOP and workflow optimization.

Usage:
    python mission_debriefing.py [--session-id SESSION_ID] [--output-dir DIR]
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
                line.strip() for line in result.stdout.strip().split("\n") if line.strip()
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
        "Review manual steps in PFC/RTB that could be automated",
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
    suggestions = generate_improvement_suggestions(git_activity, reflections, friction)
    
    # Build debrief markdown
    debrief_lines = [
        "# Mission Debriefing",
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
        debrief_lines.extend([
            "### Git Activity",
            f"- **Commits**: {len(git_activity['commits'])}",
            f"- **Files Changed**: {git_activity['files_changed']}",
            f"- **Lines Added**: {git_activity['insertions']}",
            f"- **Lines Removed**: {git_activity['deletions']}",
            "",
            "**Recent Commits**:",
        ])
        for commit in git_activity["commits"][:5]:
            debrief_lines.append(f"- `{commit}`")
        debrief_lines.append("")
    else:
        debrief_lines.extend([
            "No git activity detected in this session.",
            "",
        ])
    
    # Reflection synthesis
    debrief_lines.extend([
        "---",
        "",
        "## 2. Reflection Synthesis",
        "",
    ])
    
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
        debrief_lines.extend([
            "No reflection data available from this session.",
            "",
        ])
    
    # Improvement suggestions
    debrief_lines.extend([
        "---",
        "",
        "## 3. Improvement Suggestions",
        "",
    ])
    
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
    debrief_lines.extend([
        "---",
        "",
        "## 4. Strategic Analysis Questions",
        "",
        "### Cognitive Load Reduction",
    ])
    for item in suggestions["cognitive_load_reduction"]:
        debrief_lines.append(f"- {item}")
    debrief_lines.append("")
    
    debrief_lines.append("### Design Patterns & Refactoring")
    for item in suggestions["design_patterns"]:
        debrief_lines.append(f"- {item}")
    debrief_lines.append("")
    
    # Footer
    debrief_lines.extend([
        "---",
        "",
        "*Generated by Mission Debriefing Skill*",
        f"*{timestamp}*",
    ])
    
    debrief_content = "\n".join(debrief_lines)
    
    # Save to file
    output_file = output_dir / "debrief.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(debrief_content)
    
    return debrief_content


def main():
    parser = argparse.ArgumentParser(
        description="Generate mission debriefing after RTB completion"
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
    
    print("🎖️  Mission Debriefing")
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
