#!/bin/bash
# Trace Logger - Intent/Action/Outcome Tracking
# 
# Usage:
#   source trace.sh
#   trace "delegate to subagent" "call_subagent" "success" "output: ..."
#
# Or standalone:
#   bash trace.sh --intent "..." --action "..." --outcome "..."

TRACE_FILE="${TRACE_FILE:-.agent/session-trace.jsonl}"

trace() {
    local intent="$1"
    local action="$2"
    local outcome="$3"
    local evidence="${4:-}"
    
    mkdir -p "$(dirname "$TRACE_FILE")"
    
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Escape evidence for JSON
    evidence_escaped=$(echo "$evidence" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo "\"$evidence\"")
    
    echo "{\"timestamp\": \"$timestamp\", \"intent\": \"$intent\", \"action\": \"$action\", \"outcome\": \"$outcome\", \"evidence\": $evidence_escaped}" >> "$TRACE_FILE"
    
    echo "📝 Traced: $intent → $action [$outcome]"
}

trace_audit() {
    python3 ~/.gemini/antigravity/skills/Orchestrator/scripts/trace_logger.py audit 2>/dev/null
}

trace_verify() {
    python3 ~/.gemini/antigravity/skills/Orchestrator/scripts/trace_logger.py verify 2>/dev/null
}

# If called with arguments, log directly
if [ "$1" = "--intent" ] || [ "$1" = "-i" ]; then
    trace "$2" "$4" "$6" "$8"  # Very rough parsing
fi
