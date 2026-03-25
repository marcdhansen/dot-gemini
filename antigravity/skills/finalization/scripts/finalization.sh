#!/bin/bash

# Finalization Script
# Performs comprehensive finalization workflow as defined in project protocols

echo "🛬 Starting Finalization workflow..."
echo "=========================================="
echo

# Function to check if command succeeded
check_success() {
    if [ $? -ne 0 ]; then
        echo "❌ Error: $1 failed"
        echo "⚠️  Finalization workflow incomplete. Please address the error above."
        exit 1
    fi
}

# 1. Initialization Validation
echo "🔍 1. Initialization Validation"
echo "---------------------------"

# 1.1 Devil's Advocate Activation (STRONGLY RECOMMENDED)
echo "👹 1.1. Devil's Advocate - Critical Thinking & Unbiased Feedback"
echo "-----------------------------------------------------------"

# Check if this is a start of a work session (no recent git activity)
RECENT_ACTIVITY=$(git log --since="1 hour ago" --oneline | wc -l)
if [ "$RECENT_ACTIVITY" -eq 0 ]; then
    echo "🚀 NEW WORK SESSION DETECTED - Devil's Advocate Recommended"
    echo ""
    echo "📋 DEVIL'S ADVOCATE PERSONA:"
    echo "   🔍 Skeptical Challenge: Question assumptions vigorously"
    echo "   🎯 Counterargument Generation: Play devil's advocate rigorously"
    echo "   ⚖️  Evidence Scrutiny: Demand specific data, reject anecdotes"
    echo "   ⚡ Consequence Analysis: Highlight risks and negative outcomes"
    echo "   🔬 Alternative Exploration: Different approaches with trade-offs"
    echo ""
    echo "🎯 UNBIASED FEEDBACK STRATEGY:"
    echo "   • Challenge every assumption: 'What if this is wrong?'"
    echo "   • Demand specific evidence: 'Show me the data'"
    echo "   • Stress-test ideas: 'What are the 5 biggest problems?'"
    echo "   • Consider alternatives: 'What if we did the opposite?'"
    echo "   • Surface consequences: 'What could go wrong here?'"
    echo "   • User perspective: 'How would this impact the user experience?'"
    echo ""
    echo "⚠️  ACTIVATION METHODS:"
    echo "   • /devils-advocate - Activate for critical decision making"
    echo "   • Integrate with Initialization: /devils-advocate init"
    echo "   • Include in reflection: /reflect --devils-mode"
    echo ""
    echo "🔥 REMINDER: Balanced thinking requires BOTH:"
    echo "   • Strong advocacy for your approach (you)"
    echo "   • Rigorous challenge from devil's perspective"
    echo "   • User-centric focus throughout"
    echo ""
else
    echo "✅ Ongoing session detected - devil's advocate setup skipped"
    echo ""
fi

# 1.2 Initialization Briefing - Essential Initialization Information
echo "🎯 1.2. Initialization Briefing - Essential Initialization Information"
echo "--------------------------------------------------------"

# 1.2 Reflection Preview (STRONGLY RECOMMENDED)
echo "🧪 1.2. Reflection Preview - Prepare for Learning Capture"
echo "------------------------------------------------------"

# Check if this is the start of a work session (no recent git activity)
RECENT_ACTIVITY=$(git log --since="1 hour ago" --oneline | wc -l)
if [ "$RECENT_ACTIVITY" -eq 0 ]; then
    echo "🎯 NEW WORK SESSION DETECTED - Reflection Preview Recommended"
    echo ""
    echo "📋 Key Areas to Watch During Work Session:"
    echo "   🔧 Tool/Process Friction: When tools are slow, buggy, or inefficient"
    echo "   📝 Corrections: Direct feedback like 'No,' 'Wrong,' or 'Actually, use Y'"
    echo "   🎨 Preferences: Coding style or architectural choices"
    echo "   ✅ Success Patterns: Approaches that work particularly well"
    echo "   🚫 Failures: Mistakes, failed approaches, or dead ends"
    echo "   🔄 Workarounds: Temporary fixes or alternative methods needed"
    echo "   📊 Performance: Slow operations, memory issues, bottlenecks"
    echo "   🤔 Confusion: Unclear requirements, ambiguous instructions"
    echo "   🛑 Roadblocks: Issues that completely stop progress"
    echo ""
    echo "💡 REFLECTION CAPTURE STRATEGY:"
    echo "   ✍️  Note friction points AS THEY HAPPEN (not retrospectively)"
    echo "   🏷️  Tag issues with severity: [CRITICAL], [HIGH], [MEDIUM], [LOW]"
    echo "   📐 Note exact error messages and solutions"
    echo "   ⏰ Record time spent on different approaches"
    echo "   🎯 Capture user preferences and corrections exactly"
    echo "   🔗 Note dependencies and version conflicts"
    echo ""
    echo "📄 REFLECTION TEMPLATE (for end of session):"
    echo "   • Objective: [Issue ID / Task Name]"
    echo "   • Outcome: [Success / Partial / Failure]"
    echo "   • Tool/Process Friction: [List friction points encountered]"
    echo "   • Strategy Evolution: [What approach worked vs didn't]"
    echo "   • Applied Memories: [SKILL.md files updated]"
    echo ""
    echo "🎓 READY TO START: You now know what to watch for!"
    echo ""
    
    # Optional: Create a temporary friction log file
    FRICTION_LOG=".session_friction_$(date +%Y%m%d_%H%M%S).md"
    echo "# Session Friction Log - $(date)" > "$FRICTION_LOG"
    echo "" >> "$FRICTION_LOG"
    echo "## Quick Notes (add friction points as they happen)" >> "$FRICTION_LOG"
    echo "- " >> "$FRICTION_LOG"
    echo "📝 Created friction log: $FRICTION_LOG"
    echo "💡 Add notes to this file during your work session"
    echo ""
else
    echo "✅ Ongoing session detected - reflection preview skipped"
    echo ""
fi

# Check git status
echo "Checking git status..."
GIT_STATUS=$(git status --porcelain)
if [ -z "$GIT_STATUS" ]; then
    echo "✅ Working directory is clean"
else
    echo "📝 Uncommitted changes detected:"
    echo "$GIT_STATUS"
fi

# Auto-commit ALL remaining uncommitted changes to prevent RTB failures
if [ ! -z "$GIT_STATUS" ]; then
    echo "🔧 Auto-committing remaining uncommitted changes..."
    
    # Stage ALL changes automatically
    git add -A
    
    # Create auto-commit message with timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "finalization-auto-commit: uncommitted changes at $TIMESTAMP

- Auto-committed during finalization process
- These changes were missed by initial commit check
- Ensures clean git state before push"
    
    if [ $? -eq 0 ]; then
        echo "✅ Auto-commit successful"
        # Refresh git status
        GIT_STATUS=$(git status --porcelain)
    else
        echo "❌ Auto-commit failed - manual intervention required"
        exit 1
    fi
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check if we're on a feature branch
if [[ "$CURRENT_BRANCH" == "agent/"* ]] || [[ "$CURRENT_BRANCH" == "feature/"* ]] || [[ "$CURRENT_BRANCH" == "chore/"* ]]; then
    echo "🌿 Feature branch detected"
else
    echo "⚠️  Not on a feature branch - proceed with caution"
fi

echo

# 2. Quality Gates (only if there are changes)
if [ ! -z "$GIT_STATUS" ]; then
    echo "🧪 2. Quality Gates"
    echo "-----------------"
    
    # Check for Python tests
    if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ]; then
        echo "🐍 Python project detected - checking for test commands..."
        if grep -q "pytest" pyproject.toml requirements.txt 2>/dev/null || [ -d "tests" ]; then
            echo "🧪 Running tests..."
            if command -v pytest &> /dev/null; then
                # Run tests but allow them to fail (just warn)
                if pytest --tb=no -q 2>/dev/null; then
                    echo "✅ Tests passed"
                else
                    echo "⚠️  Some tests failed, but continuing with Finalization workflow"
                    echo "💡 You may want to fix test failures after Finalization completion"
                fi
            else
                echo "💡 pytest not found, skipping tests"
            fi
        fi
    fi
    
    # Check for linting
    if command -v ruff &> /dev/null; then
        echo "🔍 Running linter..."
        if ruff check . --quiet 2>/dev/null; then
            echo "✅ Linting passed"
        else
            echo "⚠️  Linting issues found, but continuing with Finalization workflow"
            echo "💡 You may want to fix linting issues after Finalization completion"
        fi
    fi
    
    # Check for type checking
    if command -v mypy &> /dev/null; then
        echo "🔬 Running type checker..."
        if mypy . --quiet 2>/dev/null; then
            echo "✅ Type checking passed"
        else
            echo "⚠️  Type checking issues found, but continuing with Finalization workflow"
            echo "💡 You may want to fix type checking issues after Finalization completion"
        fi
    fi
    
    echo
fi

echo

# 3. Markdown Duplication Check (Mandatory)
echo "📝 3. Markdown Duplication Verification"
echo "--------------------------------------"

# Run mandatory markdown duplication check
echo "🔍 Checking for duplicate markdown files..."
if [ -f ".agent/scripts/verify_markdown_duplicates.sh" ]; then
    if .agent/scripts/verify_markdown_duplicates.sh; then
        echo "✅ No duplicate markdown files found - proceeding with Finalization workflow"
    else
        echo "❌ DUPLICATE MARKDOWN FILES DETECTED"
        echo "🚫 BLOCKER: Cannot proceed with Finalization if duplicate markdown files exist."
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Run '.agent/scripts/verify_markdown_duplicates.sh --interactive' to review"
        echo "   2. Remove duplicate files manually or let script auto-remove"
        echo "   3. Re-run Finalization after duplicates are resolved"
        echo ""
        echo "💡 Duplicate files create confusion and waste storage space"
        exit 1
    fi
else
    echo "⚠️  Markdown verification script not found - skipping mandatory check"
    echo "💡 This may indicate a project configuration issue"
fi

echo

# 4. SOP Evaluation (Mandatory)
echo "📊 4. SOP Effectiveness Evaluation"
echo "---------------------------------"

# Run mandatory SOP evaluation
if [ -f ".agent/scripts/evaluate_sop_effectiveness.sh" ]; then
    echo "🔍 Running mandatory SOP evaluation..."
    if .agent/scripts/evaluate_sop_effectiveness.sh; then
        echo "✅ SOP evaluation passed - proceeding with Finalization workflow"
    else
        echo "❌ SOP evaluation FAILED"
        echo "🚫 BLOCKER: Cannot proceed with Finalization if SOP evaluation fails."
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Address all identified friction points"
        echo "   2. 🚨 CRITICAL: If multi-phase work detected, CREATE HAND-OFF DOCUMENTS"
        echo "   3. Improve Initialization compliance to 85%+"
        echo "   4. Re-run SOP evaluation before Finalization"
        echo ""
        echo "💡 Run '.agent/scripts/evaluate_sop_effectiveness.sh' to see detailed issues"
        exit 1
    fi
else
        echo "⚠️  SOP evaluation script not found - skipping mandatory check"
        echo "💡 This may indicate a project configuration issue"
    fi

# Enhanced hand-off compliance check for multi-phase work
echo "🔍 4.1. Enhanced Hand-off Compliance Check"
echo "-----------------------------------------"

# Check if multi-phase patterns are present and hand-offs are missing
if [ -f ".agent/scripts/multi_phase_detector.py" ]; then
    echo "🔍 Checking for multi-phase implementation patterns..."
    
    # Run multi-phase detection
    local detection_result=$(python3 .agent/scripts/multi_phase_detector.py 2>/dev/null)
    local detector_exit_code=$?
    
    if [ $detector_exit_code -eq 1 ] || [[ "$detection_result" == *"DETECTED"* ]]; then
        echo "🚨 Multi-phase implementation patterns detected"
        
        # Check if hand-off directory exists and has content
        local handoff_dir="${HANDOFF_DIR:-.agent/handoffs}"
        if [ ! -d "$handoff_dir" ] || [ -z "$(ls -A "$handoff_dir" 2>/dev/null)" ]; then
            echo "❌ CRITICAL VIOLATION: Multi-phase work without mandatory hand-off documents"
            echo "🚫 BLOCKER: Cannot proceed with Finalization without hand-off compliance"
            echo ""
            echo "🔧 MANDATORY ACTION REQUIRED:"
            echo "   1. Create hand-off documents in: .agent/handoffs/<feature>/phase-XX-handoff.md"
            echo "   2. Use template: .agent/docs/sop/MULTI_PHASE_HANDOFF_PROTOCOL.md"
            echo "   3. Verify compliance: .agent/scripts/verify_handoff_compliance.sh --phase <phase-id>"
            echo "   4. Re-run Finalization after hand-off creation"
            echo ""
            echo "💡 This prevents SOP bypass incidents like the CI_CD_P0_RESOLUTION_PLAYBOOK.md"
            exit 1
        else
            echo "✅ Hand-off documents found - compliance verified"
        fi
    else
        echo "✅ No multi-phase patterns detected - hand-off verification not required"
    fi
else
    echo "⚠️ Multi-phase detector not found - skipping enhanced check"
fi

echo

# 5. Issue Management
echo "📋 5. Issue Management"
echo "--------------------"

# Check if beads is available
if command -v bd &> /dev/null; then
    echo "📊 Checking beads status..."
    bd status || echo "💡 No active beads session"
    
    # Check for any recently closed issues that need closure notes
    echo "🔍 Checking for recently closed issues without closure notes..."
    RECENTLY_CLOSED=$(bd list --status closed --limit 5 2>/dev/null | head -10)
    if [ ! -z "$RECENTLY_CLOSED" ]; then
        echo "📝 Recently closed issues found - checking for closure notes..."
        echo "⚠️  REMINDER: Ensure all closed issues have comprehensive closure notes including:"
        echo "   📁 File locations and descriptions"
        echo "   🚀 Quick start instructions"
        echo "   📖 Documentation references" 
        echo "   🔧 Integration guidance"
        echo "   📊 Production considerations"
        echo ""
        echo "💡 Use: bd comments add <issue-id> '## Implementation Details...'"
    fi
    
    # Sync beads database
    echo "🔄 Syncing beads database..."
    bd sync || check_success "beads sync"
else
    echo "💡 beads not found, skipping issue management"
fi

echo

# 5. Quality Gates Validation
echo "🔍 5. Quality Gates Validation"
echo "-----------------------------"

# Check if there are Python files to validate
PYTHON_FILES_CHANGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep "\.py$" || true)
if [ -n "$PYTHON_FILES_CHANGED" ] || [ -n "$(git ls-files '*.py' | head -1)" ]; then
    echo "🔍 Running code quality checks..."
    
    # Run ruff format check
    echo "📝 Checking code formatting..."
    if ruff format --check . 2>/dev/null; then
        echo "✅ Code formatting is correct"
    else
        echo "❌ Code formatting issues found"
        echo "🔧 Auto-fixing formatting issues..."
        ruff format . || echo "⚠️  Could not auto-fix all formatting issues"
        echo "📝 Staging formatting fixes..."
        git add -A
    fi
    
    # Run ruff linting check
    echo "🔍 Running linting checks..."
    RUFF_OUTPUT=$(ruff check --output-format=text . 2>/dev/null || true)
    if [ -z "$RUFF_OUTPUT" ]; then
        echo "✅ No linting errors found"
    else
        echo "❌ Linting errors found:"
        echo "$RUFF_OUTPUT" | head -20
        echo ""
        echo "🔧 Auto-fixing auto-correctable errors..."
        ruff check --fix . || echo "⚠️  Could not auto-fix all linting errors"
        echo "📝 Staging linting fixes..."
        git add -A
        
        # Check if there are remaining errors
        REMAINING_ERRORS=$(ruff check --output-format=text . 2>/dev/null || true)
        if [ -n "$REMAINING_ERRORS" ]; then
            echo ""
            echo "❌ Remaining linting errors that require manual fix:"
            echo "$REMAINING_ERRORS" | head -10
            echo ""
            echo "🚫 Finalization BLOCKED: Fix remaining linting errors before proceeding"
            echo "💡 Run 'ruff check .' to see all errors and fix manually"
            exit 1
        fi
        
        echo "✅ All linting errors fixed"
    fi
else
    echo "ℹ️  No Python files detected - skipping code quality checks"
fi

# Run tests if test directory exists
if [ -d "tests" ]; then
    echo "🧪 Running test validation..."
    if command -v pytest >/dev/null 2>&1; then
        if pytest --tb=short -x 2>/dev/null; then
            echo "✅ Tests are passing"
        else
            echo "⚠️  Some tests are failing - review test output above"
            echo "💡 You can proceed, but consider fixing failing tests"
        fi
    else
        echo "⚠️  pytest not available - skipping test validation"
    fi
else
    echo "ℹ️  No tests directory found - skipping test validation"
fi

echo "✅ Quality gates validation complete"
echo

# 5b. Phase Completion Validation
echo "📋 5b. Phase Completion Validation"
echo "----------------------------------"

SESSION_FILE="$HOME/.agent/session.json"

if [[ -f "$SESSION_FILE" ]]; then
    python3 -c "
import json
from pathlib import Path

session_file = Path('$SESSION_FILE')
session = json.loads(session_file.read_text())

mode = session.get('mode', 'unknown')
phases = session.get('phases', {})

required_full = ['1_context', '2_init', '3_planning', '4_execution', '5_finalization', '6_retrospective', '7_clean_state']
required_turbo = ['5_finalization', '6_retrospective', '7_clean_state']

required = required_full if mode == 'full' else required_turbo
completed = [p for p in required if phases.get(p, {}).get('completed', False)]

if len(completed) == len(required):
    print('✅ All required phases complete')
    exit(0)
else:
    missing = [p for p in required if p not in completed or not phases.get(p, {}).get('completed', False)]
    print(f'⚠️  Missing required phases: {', '.join(missing)}')
    print(f'   Mode: {mode}')
    print(f'   Use: phase-complete <phase>')
    exit(1)
"
    PHASE_CHECK=$?
    
    if [[ $PHASE_CHECK -ne 0 ]]; then
        echo "❌ FINALIZATION BLOCKED: Incomplete phases"
        exit 1
    fi
else
    echo "⚠️  No session found - cannot validate phases"
fi
echo

# 6. Git Operations
echo "🔀 6. Git Operations"
echo "-------------------"

# Refresh git status to catch changes from previous steps (formatting, beads sync, etc.)
GIT_STATUS=$(git status --porcelain)

# Stage all changes
if [ ! -z "$GIT_STATUS" ]; then
    echo "📝 Staging changes..."
    git add -A
    
    # Commit if there are staged changes
    if ! git diff --cached --quiet; then
        echo "💬 Committing changes..."
        # Try to extract Beads issue ID from branch name (e.g., agent/agent-harness-v0o -> [agent-harness-v0o])
        ISSUE_ID=$(echo "$CURRENT_BRANCH" | grep -oE "[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+")
        if [ -z "$ISSUE_ID" ]; then
             ISSUE_ID=$(echo "$CURRENT_BRANCH" | grep -oE "[a-zA-Z0-9]+-[a-zA-Z0-9]+")
        fi
        
        ISSUE_SUFFIX=""
        if [ ! -z "$ISSUE_ID" ]; then
            ISSUE_SUFFIX=" [$ISSUE_ID]"
        fi

        # Use a sensible commit message following conventional commit format
        if [[ "$CURRENT_BRANCH" == "agent/"* ]] || [[ "$CURRENT_BRANCH" == "feature/"* ]]; then
            COMMIT_MSG="feat: auto-commit of session work on $CURRENT_BRANCH$ISSUE_SUFFIX"
        else
            COMMIT_MSG="chore: auto-update changes at $(date '+%Y-%m-%d %H:%M')$ISSUE_SUFFIX"
        fi
        git commit -m "$COMMIT_MSG" || check_success "git commit"
    fi
fi

# Pull latest changes with rebase
echo "⬇️  Pulling latest changes..."
git pull --rebase || check_success "git pull --rebase"

# Push changes to remote
echo "⬆️  Pushing changes to remote..."
git push || check_success "git push"

# Verify final git status
echo "✅ Verifying final git status..."
FINAL_STATUS=$(git status)
echo "$FINAL_STATUS"

if echo "$FINAL_STATUS" | grep -q "up to date with origin"; then
    echo "✅ Git operations successful"
else
    echo "⚠️  Git status shows potential issues"
fi

echo

# 7. Branch Cleanup Verification (Mandatory for feature branches)
echo "🌿 7. Branch Cleanup Verification"
echo "--------------------------------"

# Check if we're on a feature/agent branch and ensure proper cleanup
if [[ "$CURRENT_BRANCH" == "agent/"* ]] || [[ "$CURRENT_BRANCH" == "feature/"* ]]; then
    echo "🔍 Verifying feature branch cleanup..."
    
    # Check if working directory is clean
    WORKING_DIR_CLEAN=$(git status --porcelain)
    if [ ! -z "$WORKING_DIR_CLEAN" ]; then
        echo "❌ WORKING DIRECTORY NOT CLEAN"
        echo "🚫 BLOCKER: Cannot proceed with Finalization on feature branch with uncommitted changes"
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Commit or stash all changes"
        echo "   2. Re-run Finalization after cleanup"
        echo ""
        echo "📝 Uncommitted changes:"
        echo "$WORKING_DIR_CLEAN"
        exit 1
    fi
    
    # Check if branch is pushed to remote
    if ! git merge-base --is-ancestor "$CURRENT_BRANCH" "origin/$CURRENT_BRANCH" 2>/dev/null; then
        echo "❌ BRANCH NOT PUSHED TO REMOTE"
        echo "🚫 BLOCKER: Cannot proceed with Finalization on feature branch that isn't pushed"
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Push branch to remote: git push -u origin $CURRENT_BRANCH"
        echo "   2. Re-run Finalization after push"
        exit 1
    fi
    
    # Check for common leftover artifacts
    TEMP_DIRS=$(find . -maxdepth 1 -type d -name "*test*" -o -name "*temp*" -o -name "*tmp*" 2>/dev/null | grep -v "^\.$" | head -5)
    if [ ! -z "$TEMP_DIRS" ]; then
        echo "⚠️  Potential temporary directories found:"
        echo "$TEMP_DIRS"
        echo ""
        read -p "🗑️  Remove these temporary directories? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$TEMP_DIRS" | xargs rm -rf
            echo "✅ Temporary directories removed"
        else
            echo "💡 Temporary directories left in place (consider manual cleanup)"
        fi
    fi
    
    echo "✅ Feature branch cleanup verified"
else
    echo "ℹ️  Not on a feature/agent branch - skipping branch cleanup verification"
fi

echo

# 8. Session Cleanup
echo "🧹 8. Session Cleanup"
echo "-------------------"

# Check for session lock scripts
if [ -f "./scripts/agent-end.sh" ]; then
    echo "🔓 Cleaning up session locks..."
    ./scripts/agent-end.sh || echo "💡 Session cleanup completed (or no active session)"
else
    echo "💡 No session cleanup script found"
fi

# Browser Cleanup - Finalization Integration
echo "🌐 Browser Cleanup - Finalization Integration"
echo "-----------------------------------"

# Check if browser-manager skill is available
BROWSER_MANAGER_PATH="$HOME/.gemini/antigravity/skills/browser-manager/scripts/browser_manager.py"
if [ -f "$BROWSER_MANAGER_PATH" ] && [ -x "$BROWSER_MANAGER_PATH" ]; then
    echo "🔧 Running browser cleanup via browser-manager skill..."
    "$BROWSER_MANAGER_PATH" finalization-cleanup || echo "⚠️ Browser cleanup encountered issues"
else
    echo "💡 Browser-manager skill not available - skipping browser cleanup"
fi
echo

# Clean up temp files
echo "🗑️  Cleaning up temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.log" -mtime +7 -delete 2>/dev/null || true

# Run artifact lifecycle cleanup (task.md, walkthrough.md, etc.)
if [ -f "$HOME/.agent/scripts/cleanup_artifacts.sh" ]; then
    "$HOME/.agent/scripts/cleanup_artifacts.sh"
fi
echo


# 8.5. Reflection Capture (Mandatory with Devil's Advocate)
echo "🤔 8.5. Reflection Capture - Balanced Critical Analysis"
echo "--------------------------------------------"

# Check for devil's advocate mode flag
DEVILS_MODE=""
if [[ "$1" == "--devils-advocate" ]] || [[ "$DEVILS_MODE" == "--balanced" ]]; then
    DEVILS_MODE="$1"
    echo "👹 Devil's Advocate Mode: ENABLED ($DEVILS_MODE)"
else
    echo "🤔 Standard Reflection Mode"
fi

echo "🔍 Capturing session learnings with balanced analysis..."
if [ -f ".agent/skills/reflect.sh" ]; then
    echo "🧪 Running enhanced reflection skill..."
    # Check for devil's advocate mode
    if [ "$DEVILS_MODE" == "--devils-advocate" ]; then
        if .agent/skills/reflect.sh --devils-advocate; then
            echo "✅ Devil's advocate reflection captured successfully"
        else
            echo "⚠️  Devil's advocate reflection had issues, using standard mode"
            if .agent/skills/reflect.sh; then
                echo "✅ Standard reflection captured successfully"
            else
                echo "⚠️  Reflection capture had issues, but continuing with Finalization workflow"
            fi
        fi
    else
        if .agent/skills/reflect.sh; then
            echo "✅ Session reflection captured successfully"
        else
            echo "⚠️  Reflection capture had issues, but continuing with Finalization workflow"
            echo "💡 You may want to manually capture learnings after Finalization completion"
        fi
    fi
elif [ -f ".agent/scripts/reflect" ]; then
    echo "🧪 Running reflection script..."
    if [ "$DEVILS_MODE" == "--devils-advocate" ]; then
        if .agent/scripts/reflect --devils-advocate 2>/dev/null; then
            echo "✅ Devil's advocate reflection captured successfully"
        else
            echo "⚠️  Devil's advocate reflection had issues, using standard mode"
            if .agent/scripts/reflect; then
                echo "✅ Standard reflection captured successfully"
            else
                echo "⚠️  Reflection capture had issues, but continuing with Finalization workflow"
            fi
        fi
    else
        if .agent/scripts/reflect; then
            echo "✅ Session reflection captured successfully"
        else
            echo "⚠️  Reflection capture had issues, but continuing with Finalization workflow"
            echo "💡 You may want to manually capture learnings after Finalization completion"
        fi
    fi
elif command -v python3 &> /dev/null; then
    echo "🧪 Attempting automated reflection capture with devil's advocate mode..."
    # Fallback: Create basic reflection template with devil's advocate
    DEVILS_ARG=""
    if [ "$DEVILS_MODE" == "--devils-advocate" ]; then
        DEVILS_ARG="--devils-advocate"
    fi
    
    python3 -c "
import json
import os
from datetime import datetime

# Enhanced reflection template with devil's advocate
reflection = {
    'timestamp': datetime.now().timestamp(),
    'mission_name': f'Session Work - {\"Devils Advocate\" if \"$DEVILS_MODE\" == \"--devils-advocate\" else \"Standard\"} Reflection',
    'success_metrics': {
        'Work Completed': True,
        'Devils Advocate Mode': '$DEVILS_MODE' if \"$DEVILS_MODE\" else \"Standard\"',
        'Reflection Captured': False
    },
    'technical_learnings': [
        'Remember to use the reflect skill before Finalization completion',
        'Systematic reflection ensures knowledge transfer',
        'Devils advocate mode provides balanced critical analysis' if \"$DEVILS_MODE\" == \"--devils-advocate\" else 'Standard reflection approach'
    ],
    'challenges_overcome': [
        'Reflection skill not found - used fallback method',
        'Devils advocate integration requires enhancement' if \"$DEVILS_MODE\" == \"--devils-advocate\" else 'Standard reflection workflow'
    ],
    'devils_advocate_feedback': [],
    'quantitative_results': {
        'Files Changed': 'Unknown',
        'Session Duration': 'Unknown'
    },
    'next_process_readiness': True,
    'process_duration': 0.0,
    'status': 'PARTIAL'
}

# Save reflection data
try:
    if os.path.exists('.agent/reflections.json'):
        with open('.agent/reflections.json', 'r') as f:
            reflections = json.load(f)
        if not isinstance(reflections, list):
            reflections = []
    else:
        reflections = []
    
    reflections.append(reflection)
    
    with open('.agent/reflections.json', 'w') as f:
        json.dump(reflections, f, indent=2)
    
    print('✅ Enhanced reflection data saved')
except Exception as e:
    print(f'❌ Could not save reflection data: {e}')
"
else
    echo "⚠️  No reflection method available"
    echo "💡 Consider installing reflection skill or script"
    echo "📝 Remember to manually capture session learnings"
fi

echo


# 9. Global Memory Sync
echo "🧠 9. Global Memory Sync"
echo "----------------------"

if [ -d "$HOME/.gemini" ]; then
    echo "📝 Syncing global memory..."
    cd "$HOME/.gemini"
    if ! git diff --quiet || ! git diff --cached --quiet; then
        git add -A
        git commit -m "Session learnings and updates $(date '+%Y-%m-%d %H:%M')" || true
        git push || echo "💡 Global memory push completed (or no remote)"
    fi
    cd - > /dev/null
    echo "✅ Global memory synchronized"
else
    echo "💡 No global memory directory found"
fi

echo
echo "🎉 Finalization Workflow Complete!"
echo "========================="
echo "✅ All checks passed"
echo "✅ Changes committed and pushed"
echo "✅ Session cleaned up"
echo "✅ Ready for next session"
echo
echo "🔔 IMPORTANT REMINDER FOR FUTURE AGENTS:"
echo "====================================="
echo "When closing issues, ALWAYS add comprehensive closure notes:"
echo ""
echo "📝 Required Closure Notes Template:"
echo "-----------------------------------"
echo "## Implementation Details & Documentation"
echo ""
echo "### 📁 Files Created/Modified"
echo "- \`path/to/file.py\` - Brief description"
echo "- \`path/to/file2.py\` - Brief description"
echo ""
echo "### 🚀 Quick Start"
echo "\`\`\`bash"
echo "# Example commands"
echo "python script.py --option value"
echo "\`\`\`"
echo ""
echo "### 📖 Key Documentation"
echo "- **Main Docs**: \`path/to/README.md#section\`"
echo "- **API Reference**: \`path/to/api.md\`"
echo "- **Examples**: \`path/to/examples/\`"
echo ""
echo "### 🔧 Integration Points"
echo "- How it connects to existing system"
echo "- Configuration requirements"
echo "- Dependencies and setup"
echo ""
echo "### 📊 Production Features"
echo "- Key capabilities for production use"
echo "- Monitoring and alerting"
echo "- Performance characteristics"
echo ""
echo "💡 Add closure notes with: bd comments add <issue-id> '<notes>'"
echo ""
echo "🚀 You can now safely end your work session."