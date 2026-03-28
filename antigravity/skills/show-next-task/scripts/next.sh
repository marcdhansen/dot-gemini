#!/bin/bash

# Next Task Script
# Shows what to work on next by running beads ready and providing detailed recommendations

echo "🎯 ALL Available Tasks"
echo "========================================================="
echo ""

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

# Run bd list for in-progress tasks
INPROGRESS_OUTPUT=$(bd list --status in_progress 2>/dev/null)
if [ $? -ne 0 ]; then
    INPROGRESS_OUTPUT=""
fi

# Count priorities (format is "● P0" not "[● P0]")
P0_COUNT=$(echo "$READY_OUTPUT" | grep '● P0' | wc -l | tr -d ' ')
P1_COUNT=$(echo "$READY_OUTPUT" | grep '● P1' | wc -l | tr -d ' ')
P2_COUNT=$(echo "$READY_OUTPUT" | grep '● P2' | wc -l | tr -d ' ')
P3_COUNT=$(echo "$READY_OUTPUT" | grep '● P3' | wc -l | tr -d ' ')
P4_COUNT=$(echo "$READY_OUTPUT" | grep '● P4' | wc -l | tr -d ' ')

TOTAL_COUNT=$((P0_COUNT + P1_COUNT + P2_COUNT + P3_COUNT + P4_COUNT))

# Count and show in-progress tasks
INPROGRESS_COUNT=$(echo "$INPROGRESS_OUTPUT" | grep -c 'openloop-' | tr -d ' ') || INPROGRESS_COUNT=0

if [ "$INPROGRESS_COUNT" -gt 0 ]; then
    echo "## 🔄 Currently In Progress ($INPROGRESS_COUNT tasks):"
    echo ""
    echo "$INPROGRESS_OUTPUT" | grep 'openloop-' | while IFS= read -r line; do
        # Extract task ID and description
        TASK_ID=$(echo "$line" | grep -o 'openloop-[a-zA-Z0-9.-]*' | head -1)
        DESC=$(echo "$line" | sed 's/.*openloop-[a-zA-Z0-9.-]*: //')
        
        # Extract assignee if present (JSON output has assignee field)
        if echo "$line" | grep -q '"assignee"'; then
            ASSIGNEE=$(echo "$line" | grep -o '"assignee":"[^"]*"' | sed 's/"assignee":"//' | sed 's/"$//')
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

echo "📊 Task Priority Breakdown: P0: $P0_COUNT, P1: $P1_COUNT, P2: $P2_COUNT, P3: $P3_COUNT, P4: $P4_COUNT"
echo ""

# Function to extract and format tasks by priority
format_tasks() {
    local priority=$1
    local label=$2
    local count=$(echo "$READY_OUTPUT" | grep "● $priority" | wc -l | tr -d ' ')
    
    if [ "$count" -gt 0 ]; then
        echo "## 🎯 $label ($priority):"
        echo ""
        
        # Process tasks line by line
        echo "$READY_OUTPUT" | grep "● $priority" | while IFS= read -r line; do
            # Extract task ID and description (format: ○ openloop-xxx ● P0 Title)
            TASK_ID=$(echo "$line" | grep -o 'openloop-[a-zA-Z0-9.-]*' | head -1)
            DESC=$(echo "$line" | sed 's/.*● '$priority' //')
            
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
echo "• Ready tasks: $TOTAL_COUNT | In progress: $INPROGRESS_COUNT"
echo ""
echo "## 🎯 Recommendation:"
echo ""

if [ "$P0_COUNT" -gt 0 ]; then
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
    # Extract current objective and phase from roadmap
    CURRENT_OBJ=$(grep -A 5 "## 🎯 Current Objective" "$ROADMAP_FILE" | grep -v "## 🎯" | grep -v "Status:" | grep -v "Result:" | grep -v "Next Step:" | head -1 | sed 's/^- \*\*Task\*\*: //')
    CURRENT_STATUS=$(grep "Status:" "$ROADMAP_FILE" | head -1 | sed 's/.*Status: //')
    NEXT_STEP=$(grep "Next Step:" "$ROADMAP_FILE" | head -1 | sed 's/.*Next Step: //')
    
    echo "📍 **Current Focus:** $CURRENT_OBJ"
    echo "📊 **Status:** $CURRENT_STATUS"
    if [ -n "$NEXT_STEP" ]; then
        echo "➡️ **Next Phase:** $NEXT_STEP"
    fi
    echo ""
    
    # Check for phase alignment opportunities
    if echo "$NEXT_STEP" | grep -iq "phase"; then
        echo "💡 **Phase Alignment Opportunities:**"
        echo "• Consider creating supporting tasks for the next phase"
        echo "• Look for dependencies or prerequisites in the implementation plan"
        echo "• Review if current tasks align with phase objectives"
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