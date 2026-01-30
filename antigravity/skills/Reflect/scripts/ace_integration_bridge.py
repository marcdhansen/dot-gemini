#!/usr/bin/env python3
"""
Bridge component that integrates ACE reflector outputs into the broader Reflect skill workflow.
Captures graph quality insights and feeds them into the learnings layer for systematic improvement.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add LightRAG to path
sys.path.insert(0, "/Users/marchansen/antigravity_lightrag/LightRAG")

# Import from same directory
from enhanced_reflect_system import LearningsManager


class ACEIntegrationBridge:
    """Bridge between ACE reflector outputs and Reflect skill workflow."""

    def __init__(self, learnings_dir: Optional[Path] = None):
        self.learnings_manager = LearningsManager(learnings_dir)
        self.ace_insights_dir = Path.home() / ".gemini" / "learnings" / "ace_insights"
        self.ace_insights_dir.mkdir(parents=True, exist_ok=True)

    def process_ace_reflection(
        self, query: str, response: str, insights: List[str]
    ) -> None:
        """
        Process ACE reflector insights and convert to learnings.

        Args:
            query: The original query that prompted reflection
            response: The generated response
            insights: List of insights from ACE reflector
        """
        if not insights or insights == [
            "Error: No response generated to reflect upon."
        ]:
            return

        for insight in insights:
            if insight.startswith("Error:") or insight.startswith("Reflection failed:"):
                continue  # Skip error messages

            learning = {
                "source": "ace_reflector",
                "content": {
                    "query": query,
                    "response_sample": response[:200] + "..."
                    if len(response) > 200
                    else response,
                    "insight": insight,
                    "timestamp": datetime.now().isoformat(),
                    "category": self._categorize_ace_insight(insight),
                },
                "type": "ace_quality_insight",
                "priority": self._assess_insight_priority(insight),
            }

            self.learnings_manager.add_learning(learning)

        # Also store raw ACE insights for analysis
        self._store_ace_insight_raw(query, response, insights)

    def process_graph_repair_actions(
        self, query: str, repairs: List[Dict[str, Any]]
    ) -> None:
        """
        Process ACE graph repair actions and convert to learnings.

        Args:
            query: The original query
            repairs: List of repair actions from ACE reflector
        """
        if not repairs:
            return

        # Analyze repair patterns
        repair_summary = self._analyze_repair_patterns(repairs)

        learning = {
            "source": "ace_graph_reflector",
            "content": {
                "query": query,
                "repairs": repairs,
                "summary": repair_summary,
                "timestamp": datetime.now().isoformat(),
                "severity": self._assess_repair_severity(repairs),
            },
            "type": "ace_graph_repair",
            "priority": "high" if len(repairs) > 5 else "medium",
        }

        self.learnings_manager.add_learning(learning)

        # Store raw repair data
        self._store_repair_raw(query, repairs)

    def _categorize_ace_insight(self, insight: str) -> str:
        """Categorize ACE insight for better organization."""
        insight_lower = insight.lower()

        if any(
            keyword in insight_lower
            for keyword in ["accuracy", "correct", "factual", "wrong"]
        ):
            return "accuracy_improvement"
        elif any(
            keyword in insight_lower
            for keyword in ["complete", "missing", "add", "include"]
        ):
            return "completeness_improvement"
        elif any(
            keyword in insight_lower
            for keyword in ["format", "structure", "organize", "clear"]
        ):
            return "formatting_improvement"
        elif any(
            keyword in insight_lower
            for keyword in ["context", "relevant", "focus", "specific"]
        ):
            return "context_improvement"
        else:
            return "general_quality"

    def _assess_insight_priority(self, insight: str) -> str:
        """Assess priority of ACE insight."""
        insight_lower = insight.lower()

        high_priority_keywords = [
            "error",
            "wrong",
            "incorrect",
            "fail",
            "critical",
            "major",
        ]
        medium_priority_keywords = ["improve", "better", "should", "consider", "minor"]

        if any(keyword in insight_lower for keyword in high_priority_keywords):
            return "high"
        elif any(keyword in insight_lower for keyword in medium_priority_keywords):
            return "medium"
        else:
            return "low"

    def _analyze_repair_patterns(self, repairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in graph repair actions."""
        if not repairs:
            return {"total_repairs": 0}

        action_counts = {}
        reason_patterns = {}

        for repair in repairs:
            action = repair.get("action", "unknown")
            reason = repair.get("reason", "").lower()

            action_counts[action] = action_counts.get(action, 0) + 1

            # Extract common reason patterns
            if "hallucinat" in reason:
                reason_patterns["hallucination"] = (
                    reason_patterns.get("hallucination", 0) + 1
                )
            elif "duplicate" in reason or "merge" in reason:
                reason_patterns["deduplication"] = (
                    reason_patterns.get("deduplication", 0) + 1
                )
            elif "not support" in reason or "not found" in reason:
                reason_patterns["unsupported"] = (
                    reason_patterns.get("unsupported", 0) + 1
                )

        return {
            "total_repairs": len(repairs),
            "action_breakdown": action_counts,
            "reason_patterns": reason_patterns,
            "severity": self._assess_repair_severity(repairs),
        }

    def _assess_repair_severity(self, repairs: List[Dict[str, Any]]) -> str:
        """Assess severity of graph repairs needed."""
        total = len(repairs)

        # Count deletion actions (typically more severe)
        deletions = sum(1 for r in repairs if "delete" in r.get("action", ""))

        if total > 10 or deletions > 5:
            return "critical"
        elif total > 5 or deletions > 2:
            return "high"
        elif total > 2:
            return "medium"
        else:
            return "low"

    def _store_ace_insight_raw(
        self, query: str, response: str, insights: List[str]
    ) -> None:
        """Store raw ACE insight data for pattern analysis."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.ace_insights_dir / f"ace_insight_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "insights": insights,
            "type": "reflection_insight",
        }

        filename.write_text(json.dumps(data, indent=2))

    def _store_repair_raw(self, query: str, repairs: List[Dict[str, Any]]) -> None:
        """Store raw repair data for pattern analysis."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.ace_insights_dir / f"ace_repair_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "repairs": repairs,
            "type": "graph_repair",
        }

        filename.write_text(json.dumps(data, indent=2))

    def get_ace_learning_summary(self) -> Dict[str, Any]:
        """Get summary of ACE-related learnings."""
        pending = self.learnings_manager.get_pending_learnings()

        ace_learnings = [
            l
            for l in pending
            if l.get("source") in ["ace_reflector", "ace_graph_reflector"]
        ]

        if not ace_learnings:
            return {"total": 0, "categories": {}, "priorities": {}}

        categories = {}
        priorities = {}

        for learning in ace_learnings:
            category = learning.get("content", {}).get("category", "unknown")
            priority = learning.get("priority", "medium")

            categories[category] = categories.get(category, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1

        return {
            "total": len(ace_learnings),
            "categories": categories,
            "priorities": priorities,
            "recent_insights": [
                l for l in ace_learnings if l.get("source") == "ace_reflector"
            ][-3:],
            "recent_repairs": [
                l for l in ace_learnings if l.get("source") == "ace_graph_reflector"
            ][-3:],
        }


class ACEIntegrationTest:
    """Test utilities for ACE integration."""

    @staticmethod
    def simulate_ace_reflection():
        """Simulate ACE reflection for testing."""
        bridge = ACEIntegrationBridge()

        # Sample reflection
        query = "What are the key achievements of Albert Einstein?"
        response = (
            "Albert Einstein discovered gravity and invented the light bulb in 1905."
        )
        insights = [
            "Response contains factual inaccuracies about Einstein's achievements",
            "Should include more specific details about his actual contributions",
            "Missing context about the time period and his actual work",
        ]

        bridge.process_ace_reflection(query, response, insights)
        print("✅ Simulated ACE reflection processed")

        # Sample graph repairs
        repairs = [
            {
                "action": "delete_relation",
                "source": "Einstein",
                "target": "gravity",
                "reason": "Newton discovered gravity, not Einstein",
            },
            {
                "action": "delete_entity",
                "name": "light bulb",
                "reason": "Light bulb was invented by Edison, not mentioned in source text",
            },
            {
                "action": "merge_entities",
                "sources": ["AE", "Albert E."],
                "target": "Albert Einstein",
                "reason": "Same person, should be unified",
            },
        ]

        bridge.process_graph_repair_actions(query, repairs)
        print("✅ Simulated graph repairs processed")

        # Show summary
        summary = bridge.get_ace_learning_summary()
        print(f"\n📊 ACE Learning Summary:")
        print(f"  Total learnings: {summary['total']}")
        print(f"  Categories: {summary['categories']}")
        print(f"  Priorities: {summary['priorities']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        ACEIntegrationTest.simulate_ace_reflection()
    else:
        print("Usage: python ace_integration_bridge.py test")
        print("This bridge component is typically called from other systems.")
