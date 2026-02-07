#!/usr/bin/env python3
import argparse
import sys

ROLES = {
    "sisyphus": {
        "model": "Gemini 1.5 Pro",
        "focus": "Strategy & Planning",
        "instruction": "Maintain the Task Ledger and Progress Ledger. Ensure all tasks are completed."
    },
    "hephaestus": {
        "model": "qwen2.5-coder",
        "focus": "Implementation",
        "instruction": "Execute surgical code edits. Follow the TDD cycle strictly."
    },
    "oracle": {
        "model": "Claude 3.5 Sonnet",
        "focus": "Validation & Audit",
        "instruction": "Review the implementation for security, logic errors, and SOP compliance."
    }
}

def route_task(task_type, description):
    print(f"🎯 Routing task type: {task_type}")
    
    if task_type in ["plan", "strategy", "review"]:
        role = "sisyphus"
    elif task_type in ["code", "refactor", "fix"]:
        role = "hephaestus"
    elif task_type in ["test", "audit", "validate"]:
        role = "oracle"
    else:
        role = "sisyphus"
        
    config = ROLES[role]
    print(f"✅ Recommended Role: {role.upper()}")
    print(f"🤖 Model: {config['model']}")
    print(f"🧠 Focus: {config['focus']}")
    print(f"📝 Instruction: {config['instruction']}")
    print(f"\nTask Assignment: {description}")

def main():
    parser = argparse.ArgumentParser(description="Multi-Model Task Router")
    parser.add_argument("--type", choices=["plan", "code", "test", "refactor", "audit"], required=True)
    parser.add_argument("--task", required=True)
    
    args = parser.parse_args()
    route_task(args.type, args.task)

if __name__ == "__main__":
    main()
