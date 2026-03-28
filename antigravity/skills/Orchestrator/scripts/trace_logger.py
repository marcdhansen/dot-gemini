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
    def __init__(self, trace_file: str = None):
        if trace_file is None:
            trace_file = TRACE_FILE
        # Make path absolute to avoid cwd issues
        self.trace_file = Path(trace_file).resolve()
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        # Persistent archive for cross-session history
        self.archive_file = self.trace_file.parent / "trace-archive.jsonl"

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

    def archive(self):
        """Archive current session traces to persistent storage for cross-session analysis."""
        entries = self.read()
        if not entries:
            return {"archived": 0, "message": "No entries to archive"}

        # Read existing archive
        archived_entries = []
        if self.archive_file.exists():
            with open(self.archive_file, "r") as f:
                for line in f:
                    try:
                        archived_entries.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

        # Add current entries with session marker
        session_id = os.environ.get("SESSION_ID", datetime.utcnow().strftime("%Y%m%d-%H%M%S"))
        for entry in entries:
            entry["session_id"] = session_id
            archived_entries.append(entry)

        # Write back
        with open(self.archive_file, "w") as f:
            for entry in archived_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Clear current trace file
        self.trace_file.unlink(missing_ok=True)

        return {"archived": len(entries), "total": len(archived_entries)}

    def get_history(self, limit: int = 100) -> list:
        """Get archived trace history for cross-session analysis."""
        if not self.archive_file.exists():
            return []

        entries = []
        with open(self.archive_file, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        return entries[-limit:]

    def get_patterns(self) -> dict:
        """Analyze archived traces for patterns (recurring issues, frequent actions, etc.)."""
        history = self.get_history(limit=500)
        if not history:
            return {"message": "No history available"}

        # Count patterns
        action_counts = {}
        outcome_counts = {}
        issue_types = {}

        for entry in history:
            action = entry.get("action", "unknown")
            outcome = entry.get("outcome", "unknown")

            action_counts[action] = action_counts.get(action, 0) + 1
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

            # Track outcomes that indicate problems
            if "fail" in outcome.lower() or "error" in outcome.lower():
                issue_types[action] = issue_types.get(action, 0) + 1

        return {
            "total_entries": len(history),
            "action_counts": dict(sorted(action_counts.items(), key=lambda x: -x[1])[:10]),
            "outcome_counts": outcome_counts,
            "problem_actions": dict(sorted(issue_types.items(), key=lambda x: -x[1])[:5]),
        }

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

    def _verify_evidence(self, evidence: str, outcome: str, action: str) -> list:
        """
        Verify evidence is real, not placeholder or fabricated.

        Returns list of issues found.
        """
        issues = []
        evidence_lower = evidence.lower().strip()

        # Check for placeholder evidence
        placeholders = ["...", "n/a", "na", "none", "placeholder", "test", "todo", "tbd", "pending"]
        if evidence_lower in placeholders:
            issues.append(
                {
                    "type": "placeholder_evidence",
                    "message": f"Evidence is placeholder: '{evidence}'",
                }
            )
            return issues

        # Check for success with no meaningful output
        if outcome == "success" and len(evidence) < 5:
            issues.append(
                {
                    "type": "suspicious_success",
                    "message": f"Claimed success but evidence is minimal: '{evidence}'",
                }
            )

        # Check for evidence that claims output but is empty
        if "output:" in evidence_lower and len(evidence) < 20:
            issues.append(
                {
                    "type": "fabricated_output",
                    "message": f"Evidence claims output but is minimal: '{evidence}'",
                }
            )

        # Check for suspiciously uniform evidence (copy-paste pattern)
        entries = self.read()
        evidence_counts = {}
        for e in entries:
            ev = e.get("evidence", "")
            if ev:
                evidence_counts[ev] = evidence_counts.get(ev, 0) + 1

        # If same evidence appears 3+ times, suspicious
        if evidence and evidence_counts.get(evidence, 0) >= 3:
            issues.append(
                {
                    "type": "repetitive_evidence",
                    "message": f"Evidence repeated {evidence_counts[evidence]} times - may be fabricated",
                }
            )

        return issues

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

            # Check 4: Evidence verification - detect fake/placeholder evidence
            evidence_issues = self._verify_evidence(evidence, outcome, action)
            issues.extend(evidence_issues)

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
    subparsers.add_parser("archive", help="Archive current session traces to history")
    subparsers.add_parser("patterns", help="Show patterns from archived history")

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
    elif args.command == "archive":
        result = logger.archive()
        print(f"Archived {result['archived']} entries. Total history: {result['total']}")
    elif args.command == "patterns":
        import json

        patterns = logger.get_patterns()
        print(json.dumps(patterns, indent=2))
    elif args.command == "log":
        logger.log(args.intent, args.action, args.outcome, args.evidence)
    else:
        parser.print_help()
