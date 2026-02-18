#!/bin/bash

# Next Task Script for LightRAG
# Shows what to work on next by running beads ready and providing detailed recommendations

echo "🎯 ALL Available Tasks in the LightRAG Project"
echo "========================================================="
echo ""

# ============================================
# PHASE 0: Check for Open PRs (GitHub Source of Truth)
# ============================================
PR_SEEN=0
if command -v gh &> /dev/null; then
    PR_JSON=$(gh pr list --state open --json number,title,headRefName,createdAt,url 2>/dev/null)
    # Check if we got valid JSON output
    if [ -n "$PR_JSON" ] && [ "$PR_JSON" != "[]" ]; then
        # Filter out dependabot PRs when counting
        PR_COUNT=$(echo "$PR_JSON" | python3 -c "import sys,json; prs = [p for p in json.load(sys.stdin) if not p.get('title','').lower().startswith('dependabot') and not p.get('headRefName','').lower().startswith('dependabot/')]; print(len(prs))" 2>/dev/null || echo 0)
        
        if [ "$PR_COUNT" -gt 0 ]; then
            echo "## 🔴 OPEN PRs REQUIRING REVIEW ($PR_COUNT):"
            echo ""
            echo "$PR_JSON" | python3 -c "
import sys, json
from datetime import datetime
try:
    prs = json.load(sys.stdin)
    # Filter out dependabot PRs
    prs = [pr for pr in prs if not pr.get('title', '').lower().startswith('dependabot') and not pr.get('headRefName', '').lower().startswith('dependabot/')]
    for pr in prs:
        created = pr.get('createdAt', '')
        try:
            # Simple date parsing
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            days = (now - dt).days
            age = f'{days}d ago'
        except:
             age = '...'
        
        print(f'  🔍 PR #{pr[\"number\"]}: {pr[\"title\"]}')
        print(f'     Branch: {pr[\"headRefName\"]} | Age: {age}')
except:
    pass
"
            echo ""
            PR_SEEN=1
        fi
    fi
fi

# Fallback: Check for Beads issues with pr:open label if GH didn't show anything (or just as augmentation)
if [ "$PR_SEEN" -eq 0 ] && command -v bd &> /dev/null; then
    LABEL_OUTPUT=$(bd query "label='pr:open'" 2>/dev/null)
    if [ $? -eq 0 ] && echo "$LABEL_OUTPUT" | grep -q "Found [1-9]"; then
        LABEL_COUNT=$(echo "$LABEL_OUTPUT" | grep -o "Found [0-9]\+" | head -1 | awk '{print $NF}')
        if [ "$LABEL_COUNT" -gt 0 ]; then
             echo "## 🔴 ISSUES MARKED AS PR OPEN ($LABEL_COUNT):"
             echo ""
             echo "$LABEL_OUTPUT" | grep "^○\|^●" | while read -r line; do
                 echo "  🏷️ $line"
             done
             echo ""
             PR_SEEN=1
        fi
    fi
fi

# Get the current ready tasks from beads
if ! command -v bd &> /dev/null; then
    echo "❌ Error: 'bd' command not found. Please install beads."
    exit 1
fi

# Run beads ready and capture output
READY_OUTPUT=$(bd ready 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to run 'bd ready'. Check beads daemon status."
    exit 1
fi

# Run beads list to capture in-progress tasks
INPROGRESS_OUTPUT=$(bd list -s in_progress 2>/dev/null)
if [ $? -ne 0 ]; then
    INPROGRESS_OUTPUT=""
fi

# Count priorities
P0_COUNT=$(echo "$READY_OUTPUT" | grep '\[● P0\]' | wc -l | tr -d ' ')
P1_COUNT=$(echo "$READY_OUTPUT" | grep '\[● P1\]' | wc -l | tr -d ' ')
P2_COUNT=$(echo "$READY_OUTPUT" | grep '\[● P2\]' | wc -l | tr -d ' ')
P3_COUNT=$(echo "$READY_OUTPUT" | grep '\[● P3\]' | wc -l | tr -d ' ')
P4_COUNT=$(echo "$READY_OUTPUT" | grep '\[● P4\]' | wc -l | tr -d ' ')

TOTAL_COUNT=$((P0_COUNT + P1_COUNT + P2_COUNT + P3_COUNT + P4_COUNT))

# Count and show in-progress tasks
INPROGRESS_COUNT=$(echo "$INPROGRESS_OUTPUT" | grep -c 'agent-harness-' | tr -d ' ')

if [ "$INPROGRESS_COUNT" -gt 0 ]; then
    echo "## 🔄 Currently In Progress ($INPROGRESS_COUNT tasks):"
    echo ""
    echo "$INPROGRESS_OUTPUT" | grep '\-[a-zA-Z0-9]\+' | while IFS= read -r line; do
        # Extract task ID and description
        TASK_ID=$(echo "$line" | grep -o '[a-zA-Z0-9.-]\+-[a-zA-Z0-9.-]\+' | head -1)
        DESC=$(echo "$line" | sed "s/.*$TASK_ID: //")
        
        # Extract assignee if present
        if echo "$line" | grep -q "Assigned to:"; then
            ASSIGNEE=$(echo "$line" | grep -o "Assigned to: [^\\]*" | sed 's/Assigned to: //')
            ASSIGNEE_TEXT=" - $ASSIGNEE"
        else
            ASSIGNEE_TEXT=""
        fi
        
        echo "🔧 **$TASK_ID**: $DESC$ASSIGNEE_TEXT"
    done
    echo ""
fi

if [ "$TOTAL_COUNT" -eq 0 ]; then
    if [ "$INPROGRESS_COUNT" -gt 0 ]; then
        echo "All ready tasks are taken. Consider:"
        echo "  • Checking in-progress tasks above"
        echo "  • Creating new tasks with 'bd create'"
        echo "  • Reviewing project roadmap for new initiatives"
    else
        echo "No tasks are currently ready. Consider:"
        echo "  • Creating new tasks with 'bd create'"
        echo "  • Checking blocked tasks with 'bd blocked'"
        echo "  • Reviewing project roadmap for new initiatives"
    fi
    exit 0
fi

# Check for P0 tasks needing PR review
REVIEW_P0_TASKS=""
REVIEW_P0_COUNT=0

if [ "$INPROGRESS_COUNT" -gt 0 ]; then
    while IFS= read -r line; do
        if echo "$line" | grep -q '\[● P0\]'; then
            TASK_ID=$(echo "$line" | grep -o '[a-zA-Z0-9.-]\+-[a-zA-Z0-9.-]\+')
            if [ -n "$TASK_ID" ]; then
                # Check for PR URL in comments
                if bd show "$TASK_ID" 2>/dev/null | grep -qi "PR: http"; then
                    DESC=$(echo "$line" | sed 's/.*\[● P0\].*: //')
                    REVIEW_P0_TASKS="${REVIEW_P0_TASKS}👀 **$TASK_ID** (IN REVIEW): $DESC\n"
                    REVIEW_P0_COUNT=$((REVIEW_P0_COUNT + 1))
                fi
            fi
        fi
    done <<< "$(echo "$INPROGRESS_OUTPUT" | grep '\-[a-zA-Z0-9]\+')"
fi

if [ "$REVIEW_P0_COUNT" -gt 0 ]; then
    echo "## 🔍 NEIGHBORLY REVIEW REQUIRED (P0):"
    echo ""
    echo -e "$REVIEW_P0_TASKS"
    echo ""
fi

echo "📊 Task Priority Breakdown: P0: $P0_COUNT, P1: $P1_COUNT, P2: $P2_COUNT, P3: $P3_COUNT, P4: $P4_COUNT"
echo ""

# Function to extract and format tasks by priority
format_tasks() {
    local priority=$1
    local label=$2
    local count=$(echo "$READY_OUTPUT" | grep "\[● $priority\]" | wc -l | tr -d ' ')
    
    if [ "$count" -gt 0 ]; then
        echo "## 🎯 $label ($priority):"
        echo ""
        
        # Process tasks line by line
        echo "$READY_OUTPUT" | grep "\[● $priority\]" | while IFS= read -r line; do
            # Extract task ID and description
            TASK_ID=$(echo "$line" | grep -o '[a-zA-Z0-9.-]\+-[a-zA-Z0-9.-]\+' | head -1)
            DESC=$(echo "$line" | sed "s/.*$TASK_ID: //")
            
            # Extract type if present
            if echo "$line" | grep -q "\[task\]"; then
                TYPE="Task"
            elif echo "$line" | grep -q "\[epic\]"; then
                TYPE="Epic"
            elif echo "$line" | grep -q "\[event\]"; then
                TYPE="Event"
            else
                TYPE="Item"
            fi
            
            # Extract estimate if present
            if echo "$line" | grep -q "Estimate:"; then
                ESTIMATE=$(echo "$line" | grep -o "Estimate: [^\\]*" | sed 's/Estimate: //')
                ESTIMATE_TEXT=" ($ESTIMATE)"
            else
                ESTIMATE_TEXT=""
            fi
            
            echo "**$TASK_ID** ($TYPE): $DESC$ESTIMATE_TEXT"
        done
        echo ""
    fi
}

# Show all tasks by priority
format_tasks "P0" "🚨 CRITICAL BLOCKERS"
format_tasks "P1" "⚡ HIGH PRIORITY"
format_tasks "P2" "💡 STRATEGIC DEVELOPMENT"
format_tasks "P3" "📋 PLANNED WORK"
format_tasks "P4" "📝 LOGISTICS & EVENTS"

echo ""
echo "## 📊 Summary:"
echo "• Ready tasks: $TOTAL_COUNT | In progress: $INPROGRESS_COUNT | Needs Review: $REVIEW_P0_COUNT"
echo ""
echo "## 🎯 Recommendation:"
echo ""

if [ "$PR_SEEN" -eq 1 ]; then
    echo "TOP PRIORITY: Review open PRs listed above first."
    echo "Reasoning: Unblocking teammates is the most efficient way to maintain project velocity."
elif [ "$REVIEW_P0_COUNT" -gt 0 ]; then
    echo "TOP PRIORITY: Review open PRs for P0 issues listed above first."
    echo "Reasoning: Unblocking teammates is the most efficient way to maintain project velocity."
elif [ "$P0_COUNT" -gt 0 ]; then
    echo "Start with P0 tasks first - they are blocking project progress."
elif [ "$P1_COUNT" -gt 0 ]; then
    echo "Tackle P1 tasks for maximum impact with clear deliverables."
else
    echo "Work on P2+ tasks systematically to advance project goals."
fi

echo ""
echo "## 🚀 Next Steps:"
echo "• Start recommended task: \`bd start <task-id>\`"
echo "• Or choose any task above: \`bd start <task-id>\`"
echo ""

# Add roadmap analysis and feature development suggestions
echo "## 🗺️ Roadmap Analysis & Feature Development:"
echo ""

# Check if roadmap file exists
ROADMAP_FILE=".agent/rules/ROADMAP.md"
if [ -f "$ROADMAP_FILE" ]; then
    # Extract current phase (first one with unchecked items)
    CURRENT_PHASE_HEADER=$(grep -n "^## Phase" "$ROADMAP_FILE" | head -n 1)
    
    # Try to find a phase that is partially complete or first one with [ ]
    # Group file by Phase blocks
    PHASE_BLOCKS=$(awk '/^## Phase/{if (p) print p; p=$0; next} {p=p RS $0} END{print p}' "$ROADMAP_FILE")
    
    # Logic: Find first phase with [ ]
    CURRENT_PHASE_TEXT=$(echo "$PHASE_BLOCKS" | python3 -c "
import sys
blocks = sys.stdin.read().split('## Phase')
for block in blocks[1:]:
    if '[ ]' in block:
        print('Phase' + block.split('\n')[0].strip())
        break
")
    
    if [ -z "$CURRENT_PHASE_TEXT" ]; then
        # All phases complete? Use the last one.
        CURRENT_PHASE_TEXT=$(echo "$PHASE_BLOCKS" | tail -n 1 | head -n 1 | sed 's/^## //')
    fi

    # Extract progress for this phase
    PROGRESS=$(echo "$PHASE_BLOCKS" | python3 -c "
import sys
curr = sys.argv[1]
blocks = sys.stdin.read().split('## Phase')
for block in blocks[1:]:
    title = 'Phase' + block.split('\n')[0].strip()
    if title == curr:
        done = block.count('[x]')
        todo = block.count('[ ]')
        total = done + todo
        print(f'{done}/{total} items complete')
        break
" "$CURRENT_PHASE_TEXT")

    echo "📍 **Current Focus:** $CURRENT_PHASE_TEXT"
    echo "📊 **Status:** $PROGRESS"
    echo ""
    
    # Next step: find the phase after current
    NEXT_PHASE=$(echo "$PHASE_BLOCKS" | python3 -c "
import sys
curr = sys.argv[1]
blocks = sys.stdin.read().split('## Phase')
found = False
for block in blocks[1:]:
    title = 'Phase' + block.split('\n')[0].strip()
    if found:
        print(title)
        break
    if title == curr:
        found = True
" "$CURRENT_PHASE_TEXT")

    if [ -n "$NEXT_PHASE" ]; then
        echo "➡️ **Next Phase:** $NEXT_PHASE"
        echo ""
    fi
else
    echo "⚠️ Roadmap file not found at $ROADMAP_FILE"
    echo ""
fi

# Suggest creating new issues based on roadmap
echo "🔗 **Linking New Features to Ongoing Work:**"
echo "• Review \`.agent/rules/ImplementationPlan.md\` for detailed phase breakdown"
echo "• Create supporting tasks with \`bd create\` for roadmap objectives"
echo "• Consider cross-dependencies between current tasks and roadmap phases"
echo "• Look for opportunities to create epics that span multiple phases"
echo ""

# Feature development suggestions based on task patterns
if [ "$TOTAL_COUNT" -gt 0 ]; then
    echo "🚀 **New Feature Development Suggestions:**"
    
    # Analyze task patterns
    if echo "$READY_OUTPUT" | grep -iq "test\|testing"; then
        echo "• Consider creating companion documentation tasks for test coverage"
    fi
    
    if echo "$READY_OUTPUT" | grep -iq "refactor\|cleanup"; then
        echo "• Plan follow-up performance benchmarking tasks"
    fi
    
    if echo "$READY_OUTPUT" | grep -iq "feature\|implement"; then
        echo "• Create integration testing and documentation tasks"
    fi
    
    if [ "$P2_COUNT" -gt 3 ]; then
        echo "• Consider grouping related P2 tasks into an epic for better tracking"
    fi
    
    echo ""
fi

echo "📋 **Keep the Plan Moving Forward:**"
echo "• Create new issues: \`bd create\` (interactive mode)"
echo "• Review implementation plan: \`cat .agent/rules/ImplementationPlan.md\`"
echo "• Check project status: \`git status && bd sync\`"