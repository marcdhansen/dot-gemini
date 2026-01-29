---
name: reflect
description: Analyzes the current conversation history to extract lessons, user preferences, and corrections, then updates relevant SKILL.md files to prevent repeating mistakes.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# Reflect & Improve

## Goal

Implement the "correct once, never again" philosophy by analyzing the current session for "memories"—specific corrections, coding preferences, or logic improvements—and permanently documenting them into the relevant `SKILL.md` files.

## 🛠️ Tools & Scripts

### 1. `reflect_assistant.py` (Experimental)

Helper script for automating memory discovery and rule auditing.

**Usage**:

```bash
# Discover potential memories from a conversation log
python scripts/reflect_assistant.py discover conversation.log

# Audit a proposed rule for conflicts
python scripts/reflect_assistant.py audit "Always use YAML" .
```

## Workflow

### 1. Analyze the Session

Scan the conversation history (system prompts, user inputs, and your outputs) to identify:

* **Corrections:** Instances where the user said "No," "Wrong," "Don't do X," or "Actually, use Y."
* **Preferences:** Explicit instructions regarding coding style, naming conventions, or output formats (e.g., "Use `const` instead of `var`," "Always check for SQL injections").
* **Success Patterns:** Approaches that elicited positive feedback.
* **Mission Diagnostics:**
  * **PFC/RTB Failures:** Analyze `Flight Director` logs for repeated warnings or errors (e.g., beads sync issues, missing documentation).
  * **Tool Friction:** Note instances where tools failed or were used inefficiently (e.g., repetitive `ls` calls when `Glob` would have worked).
  * **Cleanup Oversights:** Identify temporary files or processes that were not properly terminated during RTB.

### 2. Categorize Findings

Classify identified items by confidence level:

* **High Confidence:** Explicit user instructions or hard rules (e.g., "Never use default HTML buttons").
* **Medium Confidence:** Implicit patterns that worked well during the session or mission diagnostic findings.
* **Low Confidence:** Observations that may require user verification before codifying.

### 3. Locate Target Skills

Identify which existing skill governs the relevant domain.

* Use file listing tools to find the correct skill directory (e.g., if the correction was about React components, locate `react/SKILL.md` or `frontend/SKILL.md`).
* If no specific skill exists, propose creating a new one or adding to a general `coding-standards` skill.
* **Process Improvements:** Updates to `FlightDirector/SKILL.md` or global SOP in `GEMINI.md`.

### 4. Propose Updates

Formulate an update that integrates the new learning into the target `SKILL.md`.

* **Do not** delete existing instructions unless they explicitly conflict with the new learning.
* **Do** use clear, imperative language (e.g., "Always validate inputs for X").
* **Present the Change:** Show the user a summary or diff of the proposed changes. Ask: "I have identified the following improvements. Shall I apply these changes?"

### 5. Execution & Versioning

Upon user approval:

1. **Edit:** Use the `Edit` tool to append or modify the `SKILL.md` file.
2. **Commit (Optional):** If the skills directory is a Git repository, commit the change with a message: `docs(skills): update [skill name] with session learnings`.

## Examples

**User:** "/reflect"
**Model:** "I noticed that earlier you corrected my use of `var`, preferring `const` and `let`. I also see you prefer arrow functions for components. I propose updating `javascript/SKILL.md` with these rules. Shall I proceed?"

**User:** "/reflect The button styles were wrong."
**Model:** "Understood. Scanning session for button style corrections... I see you requested `rounded-md` and `px-4`. I will add this to the 'UI Guidelines' section of `frontend/SKILL.md`."

### 6. Post-Mission Debrief

At the conclusion of a task or session (RTB):

1. **Summarize Work**: Provide a clear list of what was accomplished (Beads issues closed).
2. **Execution Stats**: Note any tool failures, significant latencies, or repetitive steps.
3. **Lessons Learned**: Highlight key discoveries or pattern shifts.
4. **Strategy Evolution**: Propose rule updates for `GEMINI.md` or other skills.
5. **Next Steps**: Explicitly list specific Beads issues created or remaining.

## 📋 Mission Reflection Template

Use this structure when performing a "/reflect" during or after a mission:

* **Objective**: [Issue ID] - [Brief Summary]
* **Mission Outcome**: [Success / Partial / Failure]
* **Tool Friction**: [e.g., "bd sync failed due to git add", "markdownlint not in path"]
* **Process Gaps**: [e.g., "No check for X before step Y"]
* **Strategy Evolution**: [e.g., "Always use YAML for extraction with small models"]
* **Proposed Updates**: [List of SKILL.md or GEMINI.md changes]

## Vision & Future Improvements

1. **Auto-detection of "Skill Gaps"**: Automatically identify tasks that took an unusual number of steps or manual corrections, flagging them as candidates for new skill creation.
2. **Versioning & Rollbacks**: Integrate with Git to track changes to `SKILL.md` files, allowing easy rollback of "learned" preferences that turn out to be context-specific rather than global rules.
3. **Cross-Mission Synthesis**: Develop a mechanism to analyze patterns across multiple recent sessions to identify long-term behavioral trends rather than just session-local ones.
4. **Librarian Interaction**: Coordinate with the `Librarian` skill to ensure that new rules are placed in the most relevant architectural or process document.
5. **Conflict Resolution**: Implement a "Rule Audit" to detect when a newly identified preference conflicts with existing instructions in `GEMINI.md` or other skills.
6. **Rule Tiering**: Categorize rules into `Strict` (Non-negotiable), `Guideline` (Default but flexible), and `Example` (Illustrative only).
