import sys
import os
import re

def discover_memories(conversation_file):
    """
    Analyzes a conversation log for potential self-evolution memories.
    Keywords: 'No', 'Wrong', 'Don't', 'Prefer', 'Always', 'Actually'.
    """
    if not conversation_file or not os.path.exists(conversation_file):
        print(f"Error: Conversation file '{conversation_file}' not found.")
        return

    keywords = [r"no", r"wrong", r"don't", r"prefer", r"always", r"actually", r"instead of"]
    pattern = re.compile(f"({'|'.join(keywords)})", re.IGNORECASE)

    print(f"--- 🧠 Memory Discovery: {conversation_file} ---")
    with open(conversation_file, 'r') as f:
        for i, line in enumerate(f):
            if pattern.search(line):
                print(f"Line {i+1}: {line.strip()}")
    print("--- End of Discovery ---")

def audit_conflicts(proposed_rule, rules_dir):
    """
    Checks if a proposed rule conflicts with existing SKILL.md files.
    """
    print(f"--- 🔍 Conflict Audit: '{proposed_rule}' ---")
    if not os.path.exists(rules_dir):
        print(f"Error: Rules directory '{rules_dir}' not found.")
        return

    for root, _, files in os.walk(rules_dir):
        for file in files:
            if file.endswith("SKILL.md"):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    # Simple token overlap check (can be improved with LLM)
                    words = set(proposed_rule.lower().split())
                    content_words = set(content.lower().split())
                    overlap = words.intersection(content_words)
                    if len(overlap) > 3: # Arbitrary threshold for "potential conflict"
                        print(f"Potential overlap/conflict in {path}")
                        print(f"  Shared tokens: {overlap}")
    print("--- End of Audit ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reflect_assistant.py [discover|audit] ...")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "discover":
        if len(sys.argv) < 3:
            print("Error: discover requires a conversation file path.")
        else:
            discover_memories(sys.argv[2])
    elif command == "audit":
        if len(sys.argv) < 3:
            print("Error: audit requires a proposed rule string.")
        else:
            audit_conflicts(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ".")
