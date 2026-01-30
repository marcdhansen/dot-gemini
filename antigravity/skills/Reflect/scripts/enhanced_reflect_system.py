#!/usr/bin/env python3
"""
Enhanced reflection system that integrates PFC/RTB diagnostics with conversation analysis
for comprehensive self-evolution and continuous improvement.
"""

import os
import sys
import json
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class FlightDiagnosticsAnalyzer:
    """Analyzes FlightDirector PFC/RTB outputs for process improvements."""

    def __init__(self):
        self.flight_script = (
            Path.home()
            / ".gemini"
            / "antigravity"
            / "skills"
            / "FlightDirector"
            / "scripts"
            / "check_flight_readiness.py"
        )

    def run_flight_director(self, mode: str) -> Tuple[str, int]:
        """Run FlightDirector and capture output."""
        try:
            result = subprocess.run(
                ["python3", str(self.flight_script), f"--{mode}"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            return "FlightDirector timeout", 1
        except Exception as e:
            return f"FlightDirector error: {e}", 1

    def analyze_pfc_failures(self) -> List[Dict]:
        """Analyze PFC failures for process improvements."""
        stdout, returncode = self.run_flight_director("pfc")
        if returncode == 0:
            return []

        issues = []

        # Common PFC failure patterns
        patterns = {
            "beads_failure": r"beads.*failed.*?installed.*?initialized",
            "task_md_missing": r"task\.md.*missing",
            "planning_docs_missing": r"ROADMAP\.md.*missing|ImplementationPlan\.md.*missing",
        }

        for issue_type, pattern in patterns.items():
            matches = re.findall(pattern, stdout, re.IGNORECASE | re.DOTALL)
            if matches:
                issues.append(
                    {
                        "type": issue_type,
                        "severity": "critical",
                        "description": matches[0],
                        "suggested_action": self._get_suggested_action(issue_type),
                    }
                )

        return issues

    def analyze_rtb_warnings(self) -> List[Dict]:
        """Analyze RTB warnings for process improvements."""
        stdout, returncode = self.run_flight_director("rtb")
        if returncode == 0:
            return []

        issues = []

        # Extract warnings between specific patterns
        warning_section = re.search(
            r"RTB WARNINGS.*?(?=\n\n|\n$|\Z)", stdout, re.DOTALL
        )
        if not warning_section:
            return issues

        warning_text = warning_section.group(0)

        # Common RTB warning patterns
        patterns = {
            "uncommitted_changes": r"uncommitted changes",
            "temp_artifacts": r"temporary artifacts found",
            "markdown_lint": r"markdown lint.*found",
            "pre_commit_failed": r"pre-commit.*failed",
            "documentation_coverage": r"documentation coverage.*found",
            "webui_lint": r"webui lint.*failed",
        }

        for issue_type, pattern in patterns.items():
            matches = re.findall(pattern, warning_text, re.IGNORECASE)
            if matches:
                issues.append(
                    {
                        "type": issue_type,
                        "severity": "warning",
                        "description": matches[0],
                        "suggested_action": self._get_suggested_action(issue_type),
                    }
                )

        return issues

    def _get_suggested_action(self, issue_type: str) -> str:
        """Get suggested action for issue type."""
        actions = {
            "beads_failure": "Ensure beads is installed and initialized before starting work",
            "task_md_missing": "Always run task creation/setup at start of session",
            "planning_docs_missing": "Verify .agent/rules/ contains ROADMAP.md and ImplementationPlan.md",
            "uncommitted_changes": "Commit changes before RTB or use --force if intentionally leaving work in progress",
            "temp_artifacts": "Run --clean during RTB or implement automatic cleanup",
            "markdown_lint": "Run markdownlint fixes before commit",
            "pre_commit_failed": "Fix all linting and formatting issues before RTB",
            "documentation_coverage": "Update orphaned documentation or add to .gitignore if intentional",
            "webui_lint": "Fix WebUI linting issues in lightrag_webui/ directory",
        }
        return actions.get(issue_type, "Review process and add preventive measures")


class ConversationAnalyzer:
    """Enhanced conversation analysis for memory discovery."""

    def __init__(self):
        # Enhanced keywords and patterns
        self.correction_patterns = [
            r"no[,.]?!\s+(?:that'?s|this is|it'?s)?\s+(wrong|incorrect|not right)",
            r"don'?t\s+(?:do|use|call|write|create|implement)",
            r"wrong[,.]?!\s+try",
            r"instead\s+(?:of|use|try)",
            r"(?:actually|in fact)\s+,?\s+use",
            r"(?:i|i'd|we|you'd)\s+(?:prefer|rather)",
            r"always\s+(?:use|do|check|ensure|avoid)",
            r"never\s+(?:use|do|check|ensure)",
        ]

        self.pattern = re.compile(
            f"({'|'.join(self.correction_patterns)})", re.IGNORECASE
        )

    def analyze_conversation(self, conversation_text: str) -> List[Dict]:
        """Analyze conversation text for learning opportunities."""
        memories = []
        lines = conversation_text.split("\n")

        for i, line in enumerate(lines):
            matches = self.pattern.search(line)
            if matches:
                # Extract context (2 lines before and after)
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = lines[context_start:context_end]

                memories.append(
                    {
                        "line_number": i + 1,
                        "pattern": matches.group(1),
                        "line": line.strip(),
                        "context": "\n".join(context),
                        "confidence": self._assess_confidence(line, matches.group(1)),
                        "type": self._categorize_memory(line),
                    }
                )

        return memories

    def _assess_confidence(self, line: str, pattern: str) -> str:
        """Assess confidence level of discovered memory."""
        high_confidence_patterns = [
            r"always|never",
            r"don'?t\s+(?:do|use)",
            r"wrong|incorrect",
        ]

        for high_pattern in high_confidence_patterns:
            if re.search(high_pattern, line, re.IGNORECASE):
                return "high"

        return "medium"

    def _categorize_memory(self, line: str) -> str:
        """Categorize the type of memory."""
        if re.search(r"don'?t|never|wrong", line, re.IGNORECASE):
            return "avoidance_rule"
        elif re.search(r"prefer|rather|instead", line, re.IGNORECASE):
            return "preference_rule"
        elif re.search(r"always|ensure|check", line, re.IGNORECASE):
            return "best_practice"
        else:
            return "general_learning"


class LearningsManager:
    """Manages the learnings layer for skill updates."""

    def __init__(self, learnings_dir: Optional[Path] = None):
        self.learnings_dir = learnings_dir or Path.home() / ".gemini" / "learnings"
        self.learnings_dir.mkdir(parents=True, exist_ok=True)

        self.pending_file = self.learnings_dir / "pending_learnings.json"
        self.applied_file = self.learnings_dir / "applied_learnings.json"

        # Initialize files if they don't exist
        for filepath in [self.pending_file, self.applied_file]:
            if not filepath.exists():
                filepath.write_text("[]")

    def add_learning(self, learning: Dict) -> None:
        """Add a new learning to the pending queue."""
        learnings = self._load_learnings(self.pending_file)

        # Add metadata
        learning["id"] = (
            f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(learnings)}"
        )
        learning["created_at"] = datetime.now().isoformat()
        learning["status"] = "pending"

        learnings.append(learning)
        self._save_learnings(self.pending_file, learnings)

    def get_pending_learnings(self) -> List[Dict]:
        """Get all pending learnings."""
        return self._load_learnings(self.pending_file)

    def apply_learning(self, learning_id: str) -> bool:
        """Mark a learning as applied and move to applied file."""
        pending = self._load_learnings(self.pending_file)
        applied = self._load_learnings(self.applied_file)

        for i, learning in enumerate(pending):
            if learning["id"] == learning_id:
                learning["applied_at"] = datetime.now().isoformat()
                learning["status"] = "applied"
                applied.append(learning)
                pending.pop(i)

                self._save_learnings(self.pending_file, pending)
                self._save_learnings(self.applied_file, applied)
                return True

        return False

    def _load_learnings(self, filepath: Path) -> List[Dict]:
        """Load learnings from JSON file."""
        try:
            return json.loads(filepath.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_learnings(self, filepath: Path, learnings: List[Dict]) -> None:
        """Save learnings to JSON file."""
        filepath.write_text(json.dumps(learnings, indent=2))


class EnhancedReflectSystem:
    """Main system integrating all reflection components."""

    def __init__(self):
        self.flight_analyzer = FlightDiagnosticsAnalyzer()
        self.conversation_analyzer = ConversationAnalyzer()
        self.learnings_manager = LearningsManager()

    def comprehensive_session_analysis(
        self, conversation_text: Optional[str] = None
    ) -> Dict:
        """Perform comprehensive analysis including PFC/RTB and conversation."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "flight_diagnostics": {},
            "conversation_memories": [],
            "recommended_actions": [],
        }

        # Analyze flight diagnostics
        print("🔍 Analyzing FlightDirector diagnostics...")
        pfc_issues = self.flight_analyzer.analyze_pfc_failures()
        rtb_issues = self.flight_analyzer.analyze_rtb_warnings()

        analysis["flight_diagnostics"] = {
            "pfc_failures": pfc_issues,
            "rtb_warnings": rtb_issues,
        }

        # Analyze conversation if provided
        if conversation_text:
            print("🧠 Analyzing conversation for memories...")
            memories = self.conversation_analyzer.analyze_conversation(
                conversation_text
            )
            analysis["conversation_memories"] = memories

        # Generate recommended actions
        analysis["recommended_actions"] = self._generate_recommendations(analysis)

        # Store significant findings as learnings
        self._store_significant_findings(analysis)

        return analysis

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations from analysis."""
        recommendations = []

        # Process diagnostic issues
        all_issues = (
            analysis["flight_diagnostics"]["pfc_failures"]
            + analysis["flight_diagnostics"]["rtb_warnings"]
        )

        for issue in all_issues:
            if issue["severity"] == "critical":
                recommendations.append(
                    {
                        "type": "process_improvement",
                        "priority": "high",
                        "description": f"Fix PFC failure: {issue['type']}",
                        "action": issue["suggested_action"],
                        "target_skill": "FlightDirector",
                    }
                )
            else:
                recommendations.append(
                    {
                        "type": "process_improvement",
                        "priority": "medium",
                        "description": f"Address RTB warning: {issue['type']}",
                        "action": issue["suggested_action"],
                        "target_skill": "FlightDirector",
                    }
                )

        # Process conversation memories
        for memory in analysis["conversation_memories"]:
            if memory["confidence"] == "high":
                recommendations.append(
                    {
                        "type": "skill_update",
                        "priority": "high",
                        "description": f"Add {memory['type']} from conversation",
                        "action": f"Update relevant skill with: {memory['line'][:100]}...",
                        "target_skill": self._suggest_target_skill(memory),
                    }
                )

        return recommendations

    def _suggest_target_skill(self, memory: Dict) -> str:
        """Suggest target skill for a memory."""
        content = memory["line"].lower()

        # Simple heuristic-based targeting
        if any(keyword in content for keyword in ["git", "commit", "branch", "push"]):
            return "git"
        elif any(
            keyword in content for keyword in ["python", "import", "def", "class"]
        ):
            return "python"
        elif any(
            keyword in content for keyword in ["javascript", "js", "function", "const"]
        ):
            return "javascript"
        elif any(keyword in content for keyword in ["test", "pytest", "assert"]):
            return "testing"
        else:
            return "coding-standards"

    def _store_significant_findings(self, analysis: Dict) -> None:
        """Store significant findings as learnings."""
        # Store critical PFC failures
        for issue in analysis["flight_diagnostics"]["pfc_failures"]:
            learning = {
                "source": "pfc_failure",
                "content": issue,
                "type": "process_improvement",
            }
            self.learnings_manager.add_learning(learning)

        # Store high-confidence conversation memories
        for memory in analysis["conversation_memories"]:
            if memory["confidence"] == "high":
                learning = {
                    "source": "conversation",
                    "content": memory,
                    "type": "skill_update",
                }
                self.learnings_manager.add_learning(learning)

    def print_analysis_summary(self, analysis: Dict) -> None:
        """Print formatted summary of analysis."""
        print("\n" + "=" * 60)
        print("🔍 COMPREHENSIVE SESSION ANALYSIS")
        print("=" * 60)

        # Flight diagnostics summary
        pfc_count = len(analysis["flight_diagnostics"]["pfc_failures"])
        rtb_count = len(analysis["flight_diagnostics"]["rtb_warnings"])

        print(f"\n📋 Flight Diagnostics:")
        print(f"  PFC Failures: {pfc_count}")
        print(f"  RTB Warnings: {rtb_count}")

        if pfc_count > 0:
            print(f"  Critical Issues:")
            for issue in analysis["flight_diagnostics"]["pfc_failures"]:
                print(f"    ❌ {issue['type']}: {issue['suggested_action']}")

        # Conversation memories summary
        memories = analysis["conversation_memories"]
        print(f"\n🧠 Conversation Memories:")
        print(f"  Total memories found: {len(memories)}")

        high_conf = len([m for m in memories if m["confidence"] == "high"])
        medium_conf = len([m for m in memories if m["confidence"] == "medium"])

        print(f"  High confidence: {high_conf}")
        print(f"  Medium confidence: {medium_conf}")

        # Recommended actions
        recommendations = analysis["recommended_actions"]
        print(f"\n🎯 Recommended Actions: {len(recommendations)}")

        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            priority_icon = "🔴" if rec["priority"] == "high" else "🟡"
            print(f"  {i}. {priority_icon} {rec['description']}")
            print(f"     Target: {rec['target_skill']}")

        if len(recommendations) > 5:
            print(f"  ... and {len(recommendations) - 5} more")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Enhanced reflection system")
    parser.add_argument("--analyze-conversation", help="Path to conversation file")
    parser.add_argument(
        "--flight-diagnostics",
        action="store_true",
        help="Run flight diagnostics analysis",
    )
    parser.add_argument(
        "--comprehensive", help="Path to conversation file for full analysis"
    )
    parser.add_argument(
        "--pending-learnings", action="store_true", help="Show pending learnings"
    )

    args = parser.parse_args()

    system = EnhancedReflectSystem()

    if args.comprehensive:
        conversation_text = (
            Path(args.comprehensive).read_text()
            if Path(args.comprehensive).exists()
            else None
        )
        analysis = system.comprehensive_session_analysis(conversation_text)
        system.print_analysis_summary(analysis)
    elif args.analyze_conversation:
        conversation_text = Path(args.analyze_conversation).read_text()
        memories = system.conversation_analyzer.analyze_conversation(conversation_text)
        print(f"Found {len(memories)} memories in conversation")
        for memory in memories:
            print(f"  Line {memory['line_number']}: {memory['line'][:100]}...")
    elif args.flight_diagnostics:
        pfc = system.flight_analyzer.analyze_pfc_failures()
        rtb = system.flight_analyzer.analyze_rtb_warnings()
        print(f"PFC Failures: {len(pfc)}")
        print(f"RTB Warnings: {len(rtb)}")
    elif args.pending_learnings:
        learnings = system.learnings_manager.get_pending_learnings()
        print(f"Pending learnings: {len(learnings)}")
        for learning in learnings:
            print(f"  {learning['id']}: {learning['type']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
