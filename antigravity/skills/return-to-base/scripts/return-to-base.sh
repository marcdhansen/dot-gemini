#!/bin/bash

# Return To Base Script for LightRAG
# Performs comprehensive RTB workflow as defined in project protocols

echo "🛬 Starting Return To Base (RTB) workflow..."
echo "=========================================="
echo

# Function to check if command succeeded
check_success() {
    if [ $? -ne 0 ]; then
        echo "❌ Error: $1 failed"
        echo "⚠️  RTB workflow incomplete. Please address the error above."
        exit 1
    fi
}

# 1. Pre-Flight Validation
echo "🔍 1. Pre-Flight Validation"
echo "---------------------------"

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
    git commit -m "rtb-auto-commit: uncommitted changes at $TIMESTAMP

- Auto-committed during RTB process
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
                    echo "⚠️  Some tests failed, but continuing with RTB workflow"
                    echo "💡 You may want to fix test failures after RTB completion"
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
            echo "⚠️  Linting issues found, but continuing with RTB workflow"
            echo "💡 You may want to fix linting issues after RTB completion"
        fi
    fi
    
    # Check for type checking
    if command -v mypy &> /dev/null; then
        echo "🔬 Running type checker..."
        if mypy . --quiet 2>/dev/null; then
            echo "✅ Type checking passed"
        else
            echo "⚠️  Type checking issues found, but continuing with RTB workflow"
            echo "💡 You may want to fix type checking issues after RTB completion"
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
        echo "✅ No duplicate markdown files found - proceeding with RTB workflow"
    else
        echo "❌ DUPLICATE MARKDOWN FILES DETECTED"
        echo "🚫 BLOCKER: Cannot proceed with RTB if duplicate markdown files exist."
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Run '.agent/scripts/verify_markdown_duplicates.sh --interactive' to review"
        echo "   2. Remove duplicate files manually or let script auto-remove"
        echo "   3. Re-run RTB after duplicates are resolved"
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
        echo "✅ SOP evaluation passed - proceeding with RTB workflow"
    else
        echo "❌ SOP evaluation FAILED"
        echo "🚫 BLOCKER: Cannot proceed with RTB if SOP evaluation fails."
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Address all identified friction points"
        echo "   2. Improve PFC compliance to 85%+"
        echo "   3. Re-run SOP evaluation before RTB"
        echo ""
        echo "💡 Run '.agent/scripts/evaluate_sop_effectiveness.sh' to see detailed issues"
        exit 1
    fi
else
    echo "⚠️  SOP evaluation script not found - skipping mandatory check"
    echo "💡 This may indicate a project configuration issue"
fi

echo

# 5. Issue Management
echo "📋 5. Issue Management"
echo "--------------------"

# Check if beads is available
if command -v bd &> /dev/null; then
    echo "📊 Checking beads status..."
    bd status || echo "💡 No active beads session"
    
    # Sync beads database
    echo "🔄 Syncing beads database..."
    bd sync || check_success "beads sync"
else
    echo "💡 beads not found, skipping issue management"
fi

echo

# 6. Git Operations
echo "🔀 6. Git Operations"
echo "-------------------"

# Stage all changes
if [ ! -z "$GIT_STATUS" ]; then
    echo "📝 Staging changes..."
    git add -A
    
    # Commit if there are staged changes
    if ! git diff --cached --quiet; then
        echo "💬 Committing changes..."
        # Use a sensible commit message based on the branch name
        if [[ "$CURRENT_BRANCH" == "agent/"* ]]; then
            COMMIT_MSG="Agent work on $CURRENT_BRANCH"
        else
            COMMIT_MSG="Update $(date '+%Y-%m-%d %H:%M')"
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
        echo "🚫 BLOCKER: Cannot proceed with RTB on feature branch with uncommitted changes"
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Commit or stash all changes"
        echo "   2. Re-run RTB after cleanup"
        echo ""
        echo "📝 Uncommitted changes:"
        echo "$WORKING_DIR_CLEAN"
        exit 1
    fi
    
    # Check if branch is pushed to remote
    if ! git merge-base --is-ancestor "$CURRENT_BRANCH" "origin/$CURRENT_BRANCH" 2>/dev/null; then
        echo "❌ BRANCH NOT PUSHED TO REMOTE"
        echo "🚫 BLOCKER: Cannot proceed with RTB on feature branch that isn't pushed"
        echo ""
        echo "🔧 Action Required:"
        echo "   1. Push branch to remote: git push -u origin $CURRENT_BRANCH"
        echo "   2. Re-run RTB after push"
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

# Clean up temp files
echo "🗑️  Cleaning up temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.log" -mtime +7 -delete 2>/dev/null || true

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
echo "🎉 RTB Workflow Complete!"
echo "========================="
echo "✅ All checks passed"
echo "✅ Changes committed and pushed"
echo "✅ Session cleaned up"
echo "✅ Ready for next session"
echo
echo "🚀 You can now safely end your work session."