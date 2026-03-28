#!/usr/bin/env python3
"""
Trace Logger - Intent/Action/Outcome Tracking

This module provides structured logging for agent actions to enable
trace verification and prevent silent failures.

Usage:
    from trace_logger import trace, verify_trace

    # Log an action
    trace(intent="delegate to subagent", action="call_subagent", outcome="success", evidence="...")

    # Verify at end of session
    verify_trace()
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

TRACE_FILE = os.environ.get("TRACE_FILE", ".agent/session-trace.jsonl")


class TraceLogger:
    def __init__(self, trace_file: str = TRACE_FILE):
        self.trace_file = Path(trace_file)
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, intent: str, action: str, outcome: str, evidence: str = "", details: dict = None):
        """Log an intent/action/outcome triple."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "intent": intent,
            "action": action,
            "outcome": outcome,
            "evidence": evidence,
            "details": details or {},
            "session_id": os.environ.get("SESSION_ID", "unknown"),
        }

        with open(self.trace_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def read(self):
        """Read all trace entries."""
        if not self.trace_file.exists():
            return []

        entries = []
        with open(self.trace_file, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        return entries

    def verify(self) -> dict:
        """
        Verify trace integrity: check for silent failures or workarounds.

        Returns dict with:
            - issues: list of detected problems
            - summary: human-readable summary
            - passed: bool
        """
        entries = self.read()
        issues = []

        for entry in entries:
            intent = entry.get("intent", "")
            action = entry.get("action", "")
            outcome = entry.get("outcome", "")
            evidence = entry.get("evidence", "")

            # Check 1: Did action match intent?
            # If intent mentions a tool/skill but action is different
            intent_keywords = extract_keywords(intent)
            action_keywords = extract_keywords(action)

            if intent_keywords and action_keywords:
                # Check for partial or no match
                match_ratio = len(intent_keywords & action_keywords) / max(len(intent_keywords), 1)

                # If very low match, might be a workaround
                if match_ratio < 0.3 and "fallback" not in evidence.lower():
                    issues.append(
                        {
                            "type": "intent_action_mismatch",
                            "entry": entry,
                            "message": f"Intent '{intent}' → Action '{action}' (match: {match_ratio:.0%})",
                        }
                    )

            # Check 2: Empty evidence for non-trivial outcomes
            if outcome == "success" and len(evidence) < 10:
                issues.append(
                    {
                        "type": "missing_evidence",
                        "entry": entry,
                        "message": f"Outcome '{outcome}' has no evidence",
                    }
                )

            # Check 3: Explicit failure markers
            failure_markers = ["failed", "error", "exception", "not found", "module not found"]
            if any(marker in outcome.lower() for marker in failure_markers):
                # This is good - failure was logged. But check if user was told.
                if not evidence or "told user" not in evidence.lower():
                    issues.append(
                        {
                            "type": "silent_failure",
                            "entry": entry,
                            "message": f"Failure logged but user not informed: {evidence}",
                        }
                    )

        passed = len(issues) == 0

        return {
            "issues": issues,
            "summary": f"{len(entries)} actions traced, {len(issues)} issues found",
            "passed": passed,
            "entries": entries,
        }

    def generate_audit_report(self) -> str:
        """Generate a self-report audit for the user."""
        entries = self.read()

        if not entries:
            return "No actions traced this session."

        lines = [
            "## 📋 Session Action Audit",
            "",
            "| Intent | Action | Outcome | Evidence |",
            "|-------|--------|----------|----------|",
        ]

        for e in entries:
            evidence = (
                e.get("evidence", "")[:50] + "..."
                if len(e.get("evidence", "")) > 50
                else e.get("evidence", "")
            )
            lines.append(
                f"| {e.get('intent', '')} | {e.get('action', '')} | {e.get('outcome', '')} | {evidence} |"
            )

        lines.append("")

        verification = self.verify()
        if not verification["passed"]:
            lines.append("### ⚠️ Issues Detected")
            for issue in verification["issues"]:
                lines.append(f"- {issue['message']}")

        return "\n".join(lines)


def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text."""
    # Remove common words
    stopwords = {
        "the",
        "a",
        "an",
        "to",
        "for",
        "in",
        "on",
        "at",
        "by",
        "of",
        "and",
        "or",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "am",
        "your",
        "my",
        "his",
        "her",
        "its",
        "our",
        "their",
    }

    words = text.lower().split()
    keywords = {w.strip(".,!?;:") for w in words if len(w) > 2 and w not in stopwords}
    return keywords


# Module-level convenience functions
_logger = None


def get_logger() -> TraceLogger:
    global _logger
    if _logger is None:
        _logger = TraceLogger()
    return _logger


def trace(intent: str, action: str, outcome: str, evidence: str = "", details: dict = None):
    """Log an action."""
    return get_logger().log(intent, action, outcome, evidence, details)


def verify_trace() -> dict:
    """Verify trace integrity."""
    return get_logger().verify()


def audit_report() -> str:
    """Generate self-report audit."""
    return get_logger().generate_audit_report()


if __name__ == "__main__":
    # CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description="Trace Logger")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("verify", help="Verify trace integrity")
    subparsers.add_parser("audit", help="Generate audit report")

    subparsers.add_parser("log", help="Log an entry")
    parser.add_argument("--intent", help="Intent")
    parser.add_argument("--action", help="Action taken")
    parser.add_argument("--outcome", help="Outcome")
    parser.add_argument("--evidence", help="Evidence")

    args = parser.parse_args()

    logger = get_logger()

    if args.command == "verify":
        result = logger.verify()
        print(f"Passed: {result['passed']}")
        print(result["summary"])
        for issue in result["issues"]:
            print(f"  - {issue['message']}")
    elif args.command == "audit":
        print(logger.generate_audit_report())
    elif args.command == "log":
        logger.log(args.intent, args.action, args.outcome, args.evidence)
    else:
        parser.print_help()
