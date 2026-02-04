#!/bin/bash

# Next Task Script for LightRAG
# Shows what to work on next by running beads ready and providing detailed recommendations

echo "🎯 ALL Available Tasks in the LightRAG Project"
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

# Run beads started to capture in-progress tasks
INPROGRESS_OUTPUT=$(bd started 2>/dev/null)
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
INPROGRESS_COUNT=$(echo "$INPROGRESS_OUTPUT" | grep -c 'lightrag-' | tr -d ' ')

if [ "$INPROGRESS_COUNT" -gt 0 ]; then
    echo "## 🔄 Currently In Progress ($INPROGRESS_COUNT tasks):"
    echo ""
    echo "$INPROGRESS_OUTPUT" | grep 'lightrag-' | while IFS= read -r line; do
        # Extract task ID and description
        TASK_ID=$(echo "$line" | grep -o 'lightrag-[a-zA-Z0-9]\+')
        DESC=$(echo "$line" | sed 's/.*lightrag-[a-zA-Z0-9]\+: //')
        
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
            TASK_ID=$(echo "$line" | grep -o 'lightrag-[a-zA-Z0-9]\+')
            DESC=$(echo "$line" | sed 's/.*\[● '$priority'\].*: //')
            
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