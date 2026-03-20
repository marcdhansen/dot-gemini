#!/bin/bash

# Log Progress Script
# Automates the structured appending to issue-specific progress logs

ISSUE_ID=$1
PHASE=$2
CONV_ID=$3
SUMMARY=$4

if [ -z "$ISSUE_ID" ]; then
    # Try to identify from branch
    BRANCH=$(git branch --show-current)
    if [[ "$BRANCH" == *"/"* ]]; then
        ISSUE_ID=$(echo $BRANCH | rev | cut -d'/' -f1 | rev)
    fi
fi

if [ -z "$ISSUE_ID" ]; then
    echo "❌ Error: Could not identify Issue ID. Please provide as first argument."
    exit 1
fi

LOG_PATH="$HOME/.agent/progress-logs/${ISSUE_ID}.md"
TEMPLATE_PATH="$HOME/.agent/templates/progress-log-template.md"

# Create log if it doesn't exist
if [ ! -f "$LOG_PATH" ]; then
    echo "📝 Creating new progress log for $ISSUE_ID..."
    cp "$TEMPLATE_PATH" "$LOG_PATH"
    # Basic substitution for title (very primitive, refined later)
    sed -i '' "s/{ISSUE_ID}/$ISSUE_ID/g" "$LOG_PATH"
    sed -i '' "s/{timestamp}/$(date +'%Y-%m-%dT%H:%M:%SZ')/g" "$LOG_PATH"
fi

# Here we would append the entry. For now, this script establishes the foundation.
# Future enhancement: take a markdown file as input and append it.

echo "✅ Log identified: $LOG_PATH"
echo "💡 Use '/log-progress' to append your structured entry."
