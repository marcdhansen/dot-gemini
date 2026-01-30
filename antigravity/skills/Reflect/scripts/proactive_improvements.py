#!/usr/bin/env python3
"""
Proactive improvement suggestions system.
Analyzes patterns across learnings, flight diagnostics, and system usage to suggest proactive improvements.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from enhanced_reflect_system import LearningsManager, FlightDiagnosticsAnalyzer


class ProactiveImprovementEngine:
    """Analyzes patterns to suggest proactive improvements."""

    def __init__(self):
        self.learnings_manager = LearningsManager()
        self.flight_analyzer = FlightDiagnosticsAnalyzer()
        self.suggestions_file = (
            Path.home() / ".gemini" / "learnings" / "proactive_suggestions.json"
        )
        self.suggestions_file.parent.mkdir(parents=True, exist_ok=True)

    def analyze_all_patterns(self) -> Dict[str, Any]:
        """Comprehensive pattern analysis across all data sources."""
        print("🔍 Analyzing patterns for proactive improvements...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "flight_patterns": self._analyze_flight_patterns(),
            "learning_patterns": self._analyze_learning_patterns(),
            "code_patterns": self._analyze_code_patterns(),
            "suggestions": [],
        }

        # Generate suggestions based on patterns
        analysis["suggestions"] = self._generate_proactive_suggestions(analysis)

        # Save analysis
        self._save_suggestions(analysis)

        return analysis

    def _analyze_flight_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in FlightDirector diagnostics."""
        print("  📋 Analyzing FlightDirector patterns...")

        patterns = {
            "pfc_failures": {},
            "rtb_warnings": {},
            "repeated_issues": [],
            "frequency_analysis": {},
        }

        # Get current diagnostics
        pfc_issues = self.flight_analyzer.analyze_pfc_failures()
        rtb_issues = self.flight_analyzer.analyze_rtb_warnings()

        # Analyze current issues
        for issue in pfc_issues:
            issue_type = issue["type"]
            patterns["pfc_failures"][issue_type] = (
                patterns["pfc_failures"].get(issue_type, 0) + 1
            )

        for issue in rtb_issues:
            issue_type = issue["type"]
            patterns["rtb_warnings"][issue_type] = (
                patterns["rtb_warnings"].get(issue_type, 0) + 1
            )

        # Load historical suggestions to find repeated issues
        historical_suggestions = self._load_historical_suggestions()

        # Track frequency of issues
        all_issues = pfc_issues + rtb_issues
        issue_counter = Counter([issue["type"] for issue in all_issues])
        patterns["frequency_analysis"] = dict(issue_counter)

        # Find issues that keep recurring
        for issue_type, count in issue_counter.most_common():
            if count >= 2:  # Repeated issue
                patterns["repeated_issues"].append(
                    {
                        "type": issue_type,
                        "frequency": count,
                        "severity": self._assess_issue_severity(issue_type),
                    }
                )

        return patterns

    def _analyze_learning_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in learnings."""
        print("  🧠 Analyzing learning patterns...")

        pending_learnings = self.learnings_manager.get_pending_learnings()

        patterns = {
            "total_pending": len(pending_learnings),
            "categories": defaultdict(int),
            "sources": defaultdict(int),
            "priorities": defaultdict(int),
            "trending_topics": [],
            "unapplied_high_priority": [],
        }

        # Analyze pending learnings
        for learning in pending_learnings:
            # Category analysis
            category = learning.get("content", {}).get("category", "unknown")
            patterns["categories"][category] += 1

            # Source analysis
            source = learning.get("source", "unknown")
            patterns["sources"][source] += 1

            # Priority analysis
            priority = learning.get("priority", "medium")
            patterns["priorities"][priority] += 1

            # High-priority unapplied learnings
            if priority == "high":
                patterns["unapplied_high_priority"].append(learning)

        # Find trending topics (simplified - could use more sophisticated NLP)
        content_texts = []
        for learning in pending_learnings:
            content = learning.get("content", {})
            if isinstance(content, dict):
                content_texts.extend(
                    str(v).lower() for v in content.values() if isinstance(v, str)
                )
            elif isinstance(content, str):
                content_texts.append(content.lower())

        # Simple keyword frequency for trending topics
        all_words = " ".join(content_texts).split()
        word_freq = Counter(
            word for word in all_words if len(word) > 4
        )  # Ignore short words

        patterns["trending_topics"] = word_freq.most_common(5)

        return dict(patterns)

    def _analyze_code_patterns(self) -> Dict[str, Any]:
        """Analyze code-related patterns from various sources."""
        print("  💻 Analyzing code patterns...")

        patterns = {
            "error_keywords": defaultdict(int),
            "improvement_keywords": defaultdict(int),
            "language_specific": defaultdict(int),
            "tool_usage": defaultdict(int),
        }

        # This would typically analyze code files, recent commits, etc.
        # For now, analyze learnings for code patterns
        pending_learnings = self.learnings_manager.get_pending_learnings()

        code_keywords = {
            "error": ["error", "bug", "fail", "exception", "wrong", "incorrect"],
            "improvement": ["improve", "better", "optimize", "enhance", "refactor"],
            "languages": ["python", "javascript", "typescript", "java", "go", "rust"],
            "tools": ["git", "docker", "pytest", "lint", "format", "build"],
        }

        for learning in pending_learnings:
            content = str(learning.get("content", "")).lower()

            for keyword_type, keywords in code_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        if keyword_type == "languages":
                            patterns["language_specific"][keyword] += 1
                        elif keyword_type == "tools":
                            patterns["tool_usage"][keyword] += 1
                        else:
                            patterns[f"{keyword_type}_keywords"][keyword] += 1

        return patterns

    def _generate_proactive_suggestions(
        self, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate proactive improvement suggestions based on analysis."""
        print("  💡 Generating proactive suggestions...")

        suggestions = []

        # Suggestions based on flight patterns
        flight_patterns = analysis["flight_patterns"]

        if flight_patterns["repeated_issues"]:
            for issue in flight_patterns["repeated_issues"]:
                suggestions.append(
                    {
                        "type": "process_improvement",
                        "priority": "high" if issue["frequency"] >= 3 else "medium",
                        "title": f"Fix repeated {issue['type']} issues",
                        "description": f"The {issue['type']} issue has occurred {issue['frequency']} times recently. Consider implementing automated prevention or updated training.",
                        "suggested_actions": [
                            "Update relevant skill documentation",
                            "Add automated checks in workflow",
                            "Provide additional training/guidance",
                        ],
                        "pattern_evidence": {
                            "source": "flight_diagnostics",
                            "frequency": issue["frequency"],
                            "severity": issue["severity"],
                        },
                    }
                )

        # Suggestions based on learning patterns
        learning_patterns = analysis["learning_patterns"]

        if learning_patterns["unapplied_high_priority"]:
            count = len(learning_patterns["unapplied_high_priority"])
            suggestions.append(
                {
                    "type": "learning_backlog",
                    "priority": "high",
                    "title": f"Process {count} high-priority pending learnings",
                    "description": f"There are {count} high-priority learnings waiting to be applied. Consider processing these to maintain system improvement.",
                    "suggested_actions": [
                        "Review and apply high-priority learnings",
                        "Set up automatic application for trusted sources",
                        "Schedule regular learning review sessions",
                    ],
                    "pattern_evidence": {
                        "source": "learning_analysis",
                        "high_priority_count": count,
                    },
                }
            )

        # Trending topic suggestions
        if learning_patterns["trending_topics"]:
            top_topic = learning_patterns["trending_topics"][0]
            if top_topic[1] >= 3:  # Topic appears at least 3 times
                suggestions.append(
                    {
                        "type": "topic_focus",
                        "priority": "medium",
                        "title": f"Focus area: '{top_topic[0]}'",
                        "description": f"The topic '{top_topic[0]}' appears frequently in recent learnings ({top_topic[1]} times). Consider creating dedicated guidelines or training for this area.",
                        "suggested_actions": [
                            "Create specialized skill for this topic",
                            "Update documentation with best practices",
                            "Consider automated checks for this area",
                        ],
                        "pattern_evidence": {
                            "source": "trending_analysis",
                            "topic": top_topic[0],
                            "frequency": top_topic[1],
                        },
                    }
                )

        # Code pattern suggestions
        code_patterns = analysis["code_patterns"]

        # Error pattern suggestions
        error_keywords = code_patterns["error_keywords"]
        if error_keywords:
            most_common_error = max(error_keywords.items(), key=lambda x: x[1])
            if most_common_error[1] >= 2:
                suggestions.append(
                    {
                        "type": "error_prevention",
                        "priority": "high",
                        "title": f"Prevent '{most_common_error[0]}' issues",
                        "description": f"Error type '{most_common_error[0]}' has appeared {most_common_error[1]} times. Consider preventive measures.",
                        "suggested_actions": [
                            "Add validation or checks",
                            "Update coding standards",
                            "Implement static analysis rules",
                        ],
                        "pattern_evidence": {
                            "source": "code_pattern_analysis",
                            "error_type": most_common_error[0],
                            "frequency": most_common_error[1],
                        },
                    }
                )

        return suggestions

    def _assess_issue_severity(self, issue_type: str) -> str:
        """Assess severity of issue type."""
        high_severity = ["beads_failure", "uncommitted_changes", "pre_commit_failed"]
        medium_severity = ["temp_artifacts", "markdown_lint", "documentation_coverage"]

        if issue_type in high_severity:
            return "high"
        elif issue_type in medium_severity:
            return "medium"
        else:
            return "low"

    def _save_suggestions(self, analysis: Dict[str, Any]) -> None:
        """Save proactive suggestions."""
        # Load existing suggestions
        existing_suggestions = self._load_historical_suggestions()

        # Add new analysis
        existing_suggestions.append(analysis)

        # Keep only last 30 analyses
        if len(existing_suggestions) > 30:
            existing_suggestions = existing_suggestions[-30:]

        self.suggestions_file.write_text(json.dumps(existing_suggestions, indent=2))

    def _load_historical_suggestions(self) -> List[Dict[str, Any]]:
        """Load historical suggestion analyses."""
        try:
            if self.suggestions_file.exists():
                return json.loads(self.suggestions_file.read_text())
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_top_suggestions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top proactive suggestions from recent analyses."""
        historical = self._load_historical_suggestions()

        if not historical:
            return []

        # Get the most recent analysis
        latest_analysis = historical[-1]
        return latest_analysis.get("suggestions", [])[:limit]

    def print_suggestions_summary(self, suggestions: List[Dict[str, Any]]) -> None:
        """Print formatted summary of suggestions."""
        if not suggestions:
            print("📊 No proactive suggestions at this time.")
            return

        print(f"\n💡 Proactive Improvement Suggestions ({len(suggestions)} total)")
        print("=" * 60)

        for i, suggestion in enumerate(suggestions, 1):
            priority_icon = (
                "🔴"
                if suggestion["priority"] == "high"
                else "🟡"
                if suggestion["priority"] == "medium"
                else "🟢"
            )

            print(f"\n{i}. {priority_icon} {suggestion['title']}")
            print(f"   📝 {suggestion['description']}")
            print(f"   🎯 Suggested Actions:")

            for j, action in enumerate(suggestion["suggested_actions"], 1):
                print(f"      {j}. {action}")

            print(f"   📊 Evidence: {suggestion['pattern_evidence']}")

        print("=" * 60)

    def track_suggestion_outcome(
        self, suggestion_id: str, outcome: str, notes: str = ""
    ) -> None:
        """Track outcome of implemented suggestions."""
        historical = self._load_historical_suggestions()

        for analysis in historical:
            for suggestion in analysis.get("suggestions", []):
                # Generate a simple ID from title+timestamp for matching
                if suggestion_id in suggestion.get("title", ""):
                    suggestion["outcome"] = {
                        "status": outcome,
                        "notes": notes,
                        "timestamp": datetime.now().isoformat(),
                    }
                    break

        self._save_suggestions(historical[-1])  # Save the latest analysis
        print(f"✅ Tracked outcome for suggestion: {outcome}")


def main():
    parser = argparse.ArgumentParser(
        description="Proactive improvement suggestions system"
    )
    parser.add_argument(
        "command", choices=["analyze", "suggest", "track"], help="Command to execute"
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="Number of suggestions to show"
    )
    parser.add_argument("--suggestion-id", help="ID of suggestion to track outcome")
    parser.add_argument(
        "--outcome",
        choices=["implemented", "rejected", "deferred"],
        help="Outcome of suggestion",
    )
    parser.add_argument("--notes", help="Additional notes about outcome")

    args = parser.parse_args()

    try:
        engine = ProactiveImprovementEngine()

        if args.command == "analyze":
            analysis = engine.analyze_all_patterns()
            suggestions = analysis["suggestions"]
            engine.print_suggestions_summary(suggestions)

        elif args.command == "suggest":
            suggestions = engine.get_top_suggestions(args.limit)
            engine.print_suggestions_summary(suggestions)

        elif args.command == "track":
            if not args.suggestion_id or not args.outcome:
                print("❌ --suggestion-id and --outcome required for track command")
                return 1

            engine.track_suggestion_outcome(
                args.suggestion_id, args.outcome, args.notes or ""
            )

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
