#!/usr/bin/env python3
"""
Structured Retrospective Skill - 18-Question Interrogation Protocol

Implements the 18-question retrospective with trajectory log validation.
Outputs structured JSON with per-question validation pass/fail.
"""

import argparse
import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Try to import trajectory logger for validation
try:
    from agent_harness.trajectory_logger import TrajectoryAnalyzer, TrajectoryLogger
except ImportError:
    TrajectoryAnalyzer = None
    TrajectoryLogger = None


# 18 Questions organized by category
QUESTIONS = {
    "task_outcome": [
        {
            "id": "Q1",
            "category": "task_outcome",
            "question": "Was the task completed successfully? What was the final outcome?",
            "validation": "trajectory_outcome",
        },
        {
            "id": "Q2",
            "category": "task_outcome",
            "question": "What deliverables were produced? List all files modified/created.",
            "validation": "none",
        },
        {
            "id": "Q3",
            "category": "task_outcome",
            "question": "What is the measurable success? (metrics, tests, acceptance criteria)",
            "validation": "none",
        },
    ],
    "process": [
        {
            "id": "Q4",
            "category": "process",
            "question": "Did the SOP workflow execute correctly? Which phases passed/failed?",
            "validation": "none",
        },
        {
            "id": "Q5",
            "category": "process",
            "question": "What blockers or warnings were encountered?",
            "validation": "stall_count",
        },
        {
            "id": "Q6",
            "category": "process",
            "question": "How long did each phase take? Was time tracking accurate?",
            "validation": "execution_time",
        },
    ],
    "knowledge": [
        {
            "id": "Q7",
            "category": "knowledge",
            "question": "What information was discovered during this session?",
            "validation": "none",
        },
        {
            "id": "Q8",
            "category": "knowledge",
            "question": "What assumptions were made? Were any proven wrong?",
            "validation": "none",
        },
        {
            "id": "Q9",
            "category": "knowledge",
            "question": "What documentation was missing or outdated?",
            "validation": "none",
        },
    ],
    "skills": [
        {
            "id": "Q10",
            "category": "skills",
            "question": "What skills were used effectively?",
            "validation": "tool_usage",
        },
        {
            "id": "Q11",
            "category": "skills",
            "question": "What skill gaps caused friction or rework?",
            "validation": "none",
        },
        {
            "id": "Q12",
            "category": "skills",
            "question": "What new skills should be learned or created?",
            "validation": "none",
        },
    ],
    "model": [
        {
            "id": "Q13",
            "category": "model",
            "question": "Which model(s) were used? How did they perform?",
            "validation": "model_name",
        },
        {
            "id": "Q14",
            "category": "model",
            "question": "Were there model-specific issues? (context limits, token count, reasoning)",
            "validation": "context_overflow",
        },
        {
            "id": "Q15",
            "category": "model",
            "question": "Would a different model have been better for this task?",
            "validation": "none",
        },
    ],
    "system": [
        {
            "id": "Q16",
            "category": "system",
            "question": "What system issues affected execution? (tools, permissions, infra)",
            "validation": "none",
        },
        {
            "id": "Q17",
            "category": "system",
            "question": "What would you do differently next time?",
            "validation": "none",
        },
        {
            "id": "Q18",
            "category": "system",
            "question": "What systematic improvements should be proposed?",
            "validation": "none",
        },
    ],
}

# Difficulty to mandatory question mapping
DIFFICULTY_MAPPING = {
    "trivial": ["task_outcome"],  # Q1-Q3
    "easy": ["task_outcome", "process"],  # Q1-Q6
    "medium": ["task_outcome", "process", "knowledge"],  # Q1-Q9
    "hard": ["task_outcome", "process", "knowledge", "skills"],  # Q1-Q12
    "expert": list(QUESTIONS.keys()),  # Q1-Q18 (all)
}

# Perfunctory answers that require elaboration
PERFUNCTORY_ANSWERS = {"none", "n/a", "nothing", "no issues", "good", "fine", "okay", ""}


def get_trajectory_data(session_id: str | None = None) -> dict[str, Any]:
    """Load trajectory data for validation."""
    log_dir = Path("logs/trajectories")
    if not log_dir.exists():
        return {"found": False, "trajectory": [], "stall_count": 0}

    if not TrajectoryAnalyzer:
        return {"found": False, "trajectory": [], "stall_count": 0}

    analyzer = TrajectoryAnalyzer(log_dir)
    
    # Find sessions
    sessions = sorted(log_dir.rglob("*.jsonl"))
    if session_id:
        sessions = [s for s in sessions if session_id in s.name]
    
    if not sessions:
        return {"found": False, "trajectory": [], "stall_count": 0}

    # Load most recent trajectory
    latest = sessions[-1]
    trajectory = analyzer.load(latest)
    
    # Extract metrics
    stall_count = 0
    execution_times = []
    tools_used = {}
    models_used = set()
    context_overflows = 0
    
    for entry in trajectory:
        execution_times.append(entry.get("execution_time_ms", 0))
        
        if entry.get("type") == "tool_call":
            tool = entry.get("tool", "unknown")
            tools_used[tool] = tools_used.get(tool, 0) + 1
        
        if entry.get("type") == "llm_call":
            if model := entry.get("model"):
                models_used.add(model)
        
        # Check for context overflow
        error = entry.get("error", "")
        if "context" in error.lower() or "overflow" in error.lower():
            context_overflows += 1
    
    return {
        "found": True,
        "trajectory": trajectory,
        "stall_count": stall_count,
        "total_execution_time_ms": sum(execution_times),
        "average_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
        "tools_used": tools_used,
        "models_used": list(models_used),
        "context_overflows": context_overflows,
    }


def validate_answer(question: dict[str, str], answer: str, trajectory_data: dict[str, Any]) -> tuple[bool, str]:
    """Validate a single answer against trajectory data."""
    validation_type = question.get("validation", "none")
    answer_lower = answer.lower().strip()
    
    # Perfunctory answer rejection
    if answer_lower in PERFUNCTORY_ANSWERS:
        return False, f"Perfunctory answer rejected: '{answer}' - requires elaboration"
    
    # Specific validation types
    if validation_type == "stall_count":
        if trajectory_data.get("stall_count", 0) > 0:
            if answer_lower in PERFUNCTORY_ANSWERS:
                return False, f"stall_count={trajectory_data['stall_count']} but answer is perfunctory"
        return True, "OK"
    
    if validation_type == "execution_time":
        total_time = trajectory_data.get("total_execution_time_ms", 0)
        # If execution took >5 minutes, expect time details
        if total_time > 300000 and len(answer) < 20:
            return False, "Execution took >5min, answer too brief"
        return True, "OK"
    
    if validation_type == "tool_usage":
        tools = trajectory_data.get("tools_used", {})
        if tools and answer_lower in PERFUNCTORY_ANSWERS:
            return False, f"Tools were used ({list(tools.keys())}) but answer is perfunctory"
        return True, "OK"
    
    if validation_type == "model_name":
        models = trajectory_data.get("models_used", [])
        if models and answer_lower in PERFUNCTORY_ANSWERS:
            return False, f"Models used ({models}) but answer is perfunctory"
        return True, "OK"
    
    if validation_type == "context_overflow":
        overflows = trajectory_data.get("context_overflows", 0)
        if overflows > 0 and answer_lower in PERFUNCTORY_ANSWERS:
            return False, f"Context overflows detected ({overflows}) but answer is perfunctory"
        return True, "OK"
    
    return True, "OK"


def get_mandatory_categories(difficulty: str) -> list[str]:
    """Get mandatory categories based on difficulty."""
    return DIFFICULTY_MAPPING.get(difficulty.lower(), DIFFICULTY_MAPPING["medium"])


def is_mandatory(question: dict[str, str], difficulty: str) -> bool:
    """Check if question is mandatory for given difficulty."""
    category = question.get("category", "")
    mandatory = get_mandatory_categories(difficulty)
    return category in mandatory


def ask_question_interactive(question: dict[str, str], difficulty: str, trajectory_data: dict[str, str]) -> dict[str, Any]:
    """Ask a single question interactively and validate the answer."""
    q_id = question["id"]
    is_mand = is_mandatory(question, difficulty)
    
    print(f"\n{'[MANDATORY]' if is_mand else '[OPTIONAL]'} {q_id}: {question['question']}")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        if is_mand:
            answer = input("Your answer: ").strip()
        else:
            answer = input("Your answer (or Enter to skip): ").strip()
        
        # Allow skipping optional questions
        if not is_mand and not answer:
            return {
                "id": q_id,
                "category": question["category"],
                "question": question["question"],
                "answer": "",
                "validation_pass": True,
                "validation_note": "Skipped (optional)",
                "skipped": True,
            }
        
        # Validate answer
        valid, note = validate_answer(question, answer, trajectory_data)
        
        if valid:
            return {
                "id": q_id,
                "category": question["category"],
                "question": question["question"],
                "answer": answer,
                "validation_pass": True,
                "validation_note": note,
            }
        
        if attempt < max_attempts - 1:
            print(f"  Validation failed: {note}")
            print(f"  Please provide a more detailed answer (attempt {attempt + 2}/{max_attempts})")
    
    return {
        "id": q_id,
        "category": question["category"],
        "question": question["question"],
        "answer": answer,
        "validation_pass": False,
        "validation_note": f"Failed after {max_attempts} attempts: {note}",
    }


def is_interactive() -> bool:
    """Check if we're running in interactive mode."""
    return sys.stdin.isatty()


def read_json_input() -> dict[str, Any] | None:
    """Try to read JSON input from stdin or file."""
    # Check if there's data in stdin
    if not sys.stdin.isatty():
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError:
            pass
    
    # Check for --input-file
    return None


def generate_default_answers(difficulty: str, trajectory_data: dict[str, Any]) -> dict[str, str]:
    """Generate default answers based on trajectory data for non-interactive mode."""
    tools = trajectory_data.get("tools_used", {})
    models = trajectory_data.get("models_used", [])
    stall_count = trajectory_data.get("stall_count", 0)
    
    return {
        "Q1": "Task completed based on trajectory analysis",
        "Q2": "Files modified: see trajectory for details",
        "Q3": "Success metrics captured in trajectory",
        "Q4": "SOP workflow completed",
        "Q5": f"Stall count: {stall_count}" if stall_count > 0 else "No blockers",
        "Q6": f"Total execution: {trajectory_data.get('total_execution_time_ms', 0)}ms",
        "Q7": "Information discovery captured in trajectory",
        "Q8": "Assumptions captured in trajectory",
        "Q9": "Documentation status unknown",
        "Q10": f"Tools used: {', '.join(tools.keys()) if tools else 'none'}",
        "Q11": "Skill gaps analysis needed",
        "Q12": "New skills recommendation pending",
        "Q13": f"Models used: {', '.join(models) if models else 'unknown'}",
        "Q14": "Model-specific issues analysis needed",
        "Q15": "Model selection analysis needed",
        "Q16": "System issues analysis needed",
        "Q17": "Improvements identified during analysis",
        "Q18": "Systematic improvements to be proposed",
    }


def run_retrospective(difficulty: str, session_id: str | None, json_only: bool, answers: dict[str, str] | None = None) -> dict[str, Any]:
    """Run the full 18-question retrospective."""
    # Load trajectory data
    trajectory_data = get_trajectory_data(session_id)
    
    # Initialize result
    result = {
        "session_id": session_id or "interactive",
        "task_difficulty": difficulty,
        "timestamp": datetime.now(UTC).isoformat(),
        "questions": [],
        "overall_validation_pass": True,
        "metadata": {
            "total_questions": 18,
            "mandatory_answered": 0,
            "optional_answered": 0,
            "validation_failures": 0,
            "trajectory_logged": trajectory_data.get("found", False),
            "trajectory_metrics": {
                "stall_count": trajectory_data.get("stall_count", 0),
                "total_execution_time_ms": trajectory_data.get("total_execution_time_ms", 0),
                "tools_used": trajectory_data.get("tools_used", {}),
                "models_used": trajectory_data.get("models_used", []),
            },
        },
    }
    
    # If answers provided (non-interactive), use them
    if answers:
        for category in QUESTIONS:
            for question in QUESTIONS[category]:
                q_id = question["id"]
                answer = answers.get(q_id, "")
                
                # Validate
                valid, note = validate_answer(question, answer, trajectory_data)
                
                answer_data = {
                    "id": q_id,
                    "category": question["category"],
                    "question": question["question"],
                    "answer": answer,
                    "validation_pass": valid,
                    "validation_note": note,
                }
                
                if is_mandatory(question, difficulty):
                    result["metadata"]["mandatory_answered"] += 1
                else:
                    result["metadata"]["optional_answered"] += 1
                
                if not valid:
                    result["overall_validation_pass"] = False
                    result["metadata"]["validation_failures"] += 1
                
                result["questions"].append(answer_data)
        return result
    
    # Interactive mode
    if not is_interactive():
        # Non-interactive without answers: generate defaults or require --input
        default_answers = generate_default_answers(difficulty, trajectory_data)
        return run_retrospective(difficulty, session_id, json_only, default_answers)
    
    # Ask questions by category
    for category in QUESTIONS:
        for question in QUESTIONS[category]:
            answer_data = ask_question_interactive(question, difficulty, trajectory_data)
            result["questions"].append(answer_data)
            
            # Update metadata
            if answer_data.get("skipped"):
                continue
                
            if is_mandatory(question, difficulty):
                result["metadata"]["mandatory_answered"] += 1
            else:
                result["metadata"]["optional_answered"] += 1
            
            if not answer_data.get("validation_pass", True):
                result["overall_validation_pass"] = False
                result["metadata"]["validation_failures"] += 1
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Structured Retrospective - 18-Question Protocol")
    parser.add_argument("--difficulty", default="medium", choices=["trivial", "easy", "medium", "hard", "expert"],
                        help="Task difficulty (affects mandatory questions)")
    parser.add_argument("--session-id", help="Session ID for trajectory log lookup")
    parser.add_argument("--json-only", action="store_true", help="Output only JSON (for automation)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument("--input-file", help="JSON file with pre-filled answers")
    parser.add_argument("--fallback", action="store_true", help="Use default answers (non-interactive mode)")
    
    args = parser.parse_args()
    
    # Try to load answers from file if provided
    answers = None
    if args.input_file:
        with open(args.input_file) as f:
            answers = json.load(f)
    
    # Check for stdin input
    if not is_interactive() and not answers and not args.fallback:
        # Try reading stdin
        try:
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                answers = json.loads(stdin_data)
        except:
            pass
    
    result = run_retrospective(args.difficulty, args.session_id, args.json_only, answers)
    
    # Output
    json_output = json.dumps(result, indent=2)
    
    if args.output:
        Path(args.output).write_text(json_output)
        print(f"Output written to: {args.output}")
    else:
        print(json_output)
    
    # Exit code based on validation
    sys.exit(0 if result["overall_validation_pass"] else 1)


if __name__ == "__main__":
    main()
