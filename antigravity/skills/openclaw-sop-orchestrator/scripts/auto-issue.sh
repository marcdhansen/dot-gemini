#!/bin/bash
# Auto Issue Wrapper - OpenClaw Session Co-pilot
# 
# Provides automatic session management by invoking OpenClaw at phase transitions.
# Reduces manual orchestrator commands - OpenClaw becomes a real-time assistant.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATE_SCRIPT="$SCRIPT_DIR/orchestrate.sh"
SESSION_DIR="${HOME}/GitHub/marcdhansen/agent-harness/.harness"
PROJECT_DIR="${HOME}/GitHub/marcdhansen/agent-harness"
BEADS_DIR="${PROJECT_DIR}/.beads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[auto-issue]${NC} $1"; }
log_success() { echo -e "${GREEN}[auto-issue]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[auto-issue]${NC} $1"; }
log_error() { echo -e "${RED}[auto-issue]${NC} $1"; }

# Ensure BEADS_DIR is set for all bd commands
export BEADS_DIR

# Ensure we're in the project directory for bd commands
cd "$PROJECT_DIR"

show_help() {
    cat << EOF
OpenClaw Auto Wrapper - Session Co-pilot

Usage: $(basename "$0") <command> [options]

Commands:
    start [claim]     Initialize session, check ready tasks, optionally claim first
    phase <name>     Signal phase transition (init|planning|execution|finalization|retrospective|clean)
    watch             Start background monitoring (polls every 5 min)
    end               Auto-finalize: quality gates, close issue, create handoff
    status            Show current session state
    help              Show this help

Examples:
    $(basename "$0") start              # Check ready tasks, no auto-claim
    $(basename "$0") start --claim     # Auto-claim first ready task
    $(basename "$0") phase execution   # Signal entering execution phase
    $(basename "$0") watch             # Start background monitoring
    $(basename "$0") end               # Close session with quality gates

Environment:
    BEADS_DIR         Path to beads database (default: ~/.beads)
    CHECK_INTERVAL    Watch interval in seconds (default: 300)

EOF
}

# Get current session info from session.json
get_session_info() {
    local session_file="$SESSION_DIR/session.json"
    if [ -f "$session_file" ]; then
        cat "$session_file"
    else
        echo "{}"
    fi
}

# Get current phase from session
get_current_phase() {
    local session_info=$(get_session_info)
    echo "$session_info" | grep -o '"phase":"[^"]*"' | cut -d'"' -f4 || echo "unknown"
}

# Get current issue from session
get_current_issue() {
    local session_info=$(get_session_info)
    echo "$session_info" | grep -o '"issue_id":"[^"]*"' | cut -d'"' -f4 || echo ""
}

# Command: start
cmd_start() {
    local auto_claim=false
    if [ "$1" = "--claim" ] || [ "$1" = "-c" ]; then
        auto_claim=true
    fi
    
    log_info "Starting auto session..."
    
    # Check if session already exists
    local current_issue=$(get_current_issue)
    if [ -n "$current_issue" ]; then
        log_warn "Session already active with issue: $current_issue"
        log_info "Use 'status' to see current state"
        return 0
    fi
    
    # Get next task recommendation
    log_info "Getting next task recommendation..."
    
    # Try OpenClaw first (with 60s timeout), fall back to direct bd
    local output
    local openclaw_failed=false
    
    if [ -n "$FORCE_OPENCLAW" ]; then
        # Force OpenClaw mode (ignores timeout)
        log_info "FORCE_OPENCLAW set - trying OpenClaw..."
        output=$("$ORCHESTRATE_SCRIPT" next 2>&1) || openclaw_failed=true
    else
        # Default: use timeout
        log_info "Trying OpenClaw (60s timeout)..."
        output=$(timeout 60 "$ORCHESTRATE_SCRIPT" next 2>&1) || openclaw_failed=true
        
        if [ $? -eq 124 ]; then
            log_warn "OpenClaw timed out after 60s"
            openclaw_failed=true
        fi
    fi
    
    # Fall back to direct bd if OpenClaw failed
    if [ "$openclaw_failed" = true ] || echo "$output" | grep -qi "billing error\|timeout\|Error\|timed out"; then
        log_info "Using fallback: direct bd..."
        output=$(cd "$PROJECT_DIR" && bd ready --json 2>&1)
        echo "$output"
        log_info "Run 'bd update <issue-id> --claim' to claim a task"
    else
        echo "$output"
    fi
    
    if [ "$auto_claim" = true ]; then
        # Extract recommended issue ID from output (look for pattern like "agent-uzjl")
        local recommended=$(echo "$output" | grep -oE 'agent-[a-z]{2,4}[0-9a-z]*' | head -1)
        
        # If extraction failed, try alternative patterns
        if [ -z "$recommended" ]; then
            recommended=$(echo "$output" | grep -oE 'bd update [a-z0-9.-]+' | awk '{print $3}' | head -1)
        fi
        
        if [ -n "$recommended" ]; then
            log_info "Auto-claiming recommended issue: $recommended"
            if bd update "$recommended" --claim --json 2>&1; then
                log_success "Claimed $recommended"
                
                # Update session.json
                mkdir -p "$SESSION_DIR"
                cat > "$SESSION_DIR/session.json" << EOF
{
    "issue_id": "$recommended",
    "phase": "init",
    "started_at": "$(date -Iseconds)",
    "auto_mode": true
}
EOF
                log_success "Created session.json with issue $recommended"
            else
                log_warn "Failed to claim $recommended"
            fi
        else
            log_warn "Could not extract issue ID from output"
            log_info "Please claim manually: bd update <issue-id> --claim"
        fi
    fi
    
    log_success "Session initialized in auto mode"
}

# Command: phase
cmd_phase() {
    local phase="$1"
    
    if [ -z "$phase" ]; then
        log_error "Phase name required"
        log_info "Usage: $(basename "$0") phase <init|planning|execution|finalization|retrospective|clean>"
        exit 1
    fi
    
    local current_issue=$(get_current_issue)
    local current_phase=$(get_current_phase)
    
    log_info "Transitioning from '$current_phase' to '$phase'..."
    
    # Update or create session.json
    local session_file="$SESSION_DIR/session.json"
    mkdir -p "$SESSION_DIR"
    
    if [ -f "$session_file" ]; then
        # Update phase in existing file (macOS compatible)
        sed -i '' "s/\"phase\": \"[^\"]*\"/\"phase\": \"$phase\"/" "$session_file" 2>/dev/null || \
        sed -i "s/\"phase\": \"[^\"]*\"/\"phase\": \"$phase\"/" "$session_file" 2>/dev/null || true
    else
        # Create new session file
        cat > "$session_file" << EOF
{
    "issue_id": "$current_issue",
    "phase": "$phase",
    "started_at": "$(date -Iseconds)",
    "auto_mode": true
}
EOF
    fi
    
    # Run OpenClaw validation for this phase
    log_info "Running OpenClaw validation for $phase phase..."
    local output=$("$ORCHESTRATE_SCRIPT" validate "$phase" 2>&1)
    echo "$output"
    
    # Phase-specific suggestions
    case "$phase" in
        init)
            log_info "💡 Reminder: Initialize session with 'bd update <id> --claim'"
            ;;
        planning)
            log_info "💡 Reminder: Get explicit approval before execution"
            ;;
        execution)
            log_info "💡 Remember: Follow TDD (Red → Green → Refactor)"
            ;;
        finalization)
            log_info "💡 Run quality gates, commit, create PR"
            ;;
        retrospective)
            log_info "💡 Run /reflect to capture learnings"
            ;;
        clean)
            log_info "💡 Verify git status clean, delete temp files"
            ;;
    esac
    
    log_success "Phase transition complete: $phase"
}

# Command: watch (background monitoring)
cmd_watch() {
    local interval="${CHECK_INTERVAL:-300}"  # Default 5 minutes
    
    log_info "Starting background monitoring (every ${interval}s)..."
    log_info "Press Ctrl+C to stop"
    
    local last_phase=""
    
    while true; do
        clear
        echo "=== OpenClaw Auto Watch $(date) ==="
        echo ""
        
        # Check session state
        local current_phase=$(get_current_phase)
        local current_issue=$(get_current_issue)
        
        echo "Current Phase: $current_phase"
        echo "Current Issue: $current_issue"
        echo ""
        
        # Run status check
        "$ORCHESTRATE_SCRIPT" status 2>&1 | head -30
        
        # Check for phase reminders
        if [ "$current_phase" != "$last_phase" ]; then
            case "$current_phase" in
                execution)
                    log_warn "⚠️ In execution phase - remember TDD"
                    ;;
                finalization)
                    log_warn "⚠️ Ready to finalize - run quality gates"
                    ;;
                retrospective)
                    log_warn "⚠️ Run /reflect before closing"
                    ;;
            esac
            last_phase="$current_phase"
        fi
        
        echo ""
        echo "Sleeping ${interval}s... (Ctrl+C to stop)"
        sleep "$interval"
    done
}

# Command: end (auto-finalize)
cmd_end() {
    local current_issue=$(get_current_issue)
    local current_phase=$(get_current_phase)
    
    log_info "Starting auto-finalization..."
    
    # Run close command (includes quality gates, handoff, reflect)
    log_info "Running session close..."
    local output=$("$ORCHESTRATE_SCRIPT" close 2>&1)
    echo "$output"
    
    # Clear session
    if [ -f "$SESSION_DIR/session.json" ]; then
        rm "$SESSION_DIR/session.json"
    fi
    
    log_success "Session closed and cleaned up"
    log_info "Run '/issue next' to start next session"
}

# Command: status
cmd_status() {
    local current_phase=$(get_current_phase)
    local current_issue=$(get_current_issue)
    
    echo "=== Auto Issue Session Status ==="
    echo "Phase: $current_phase"
    echo "Issue: $current_issue"
    echo "Mode: Auto"
    echo ""
    
    # Run full status
    "$ORCHESTRATE_SCRIPT" status 2>&1
}

# Main
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    start)
        cmd_start "$@"
        ;;
    phase)
        cmd_phase "$@"
        ;;
    watch)
        cmd_watch "$@"
        ;;
    end)
        cmd_end "$@"
        ;;
    status)
        cmd_status "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac