#!/bin/bash

# Artifact Cleanup Script
# Removes temporary session artifacts after issue delivery or session close

echo "🧹 Starting Artifact Cleanup..."

TARGET_FILES=(
    "task.md"
    "walkthrough.md"
    "debrief.md"
)

# Remove matched session friction logs
FRICTION_LOGS=$(ls .session_friction_*.md 2>/dev/null)

for file in "${TARGET_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "🗑️  Removing $file"
        rm "$file"
    fi
done

if [ ! -z "$FRICTION_LOGS" ]; then
    for log in $FRICTION_LOGS; do
        echo "🗑️  Removing $log"
        rm "$log"
    done
fi

echo "✅ Artifact cleanup complete."
