---
name: browser-manager
description: Manages Playwright browser processes and tabs with soft warnings, automatic cleanup, and cross-agent coordination.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# 🌐 Browser Manager Skill

**Purpose**: Centralized Playwright browser process lifecycle management with tab tracking, soft warnings, and automatic cleanup.

## 🎯 Mission

- Track Playwright-managed browsers and their tabs
- Provide configurable resource limits (no defaults)
- Enforce soft warnings for resource usage
- Enable cross-agent cleanup with user permission
- Automatic session cleanup at mission end
- Maintain browser ownership tracking

## 🛠️ Tools & Scripts

### Core Browser Management

```bash
# Check current browser and tab status
browser-manager status

# Show detailed tab information  
browser-manager tabs

# Clean up your browsers
browser-manager cleanup

# Clean specific agent's browsers (requires permission)
browser-manager cleanup --agent <agent-id>

# Clean all browsers (requires permission for each agent)
browser-manager cleanup --all
```

### Configuration Management

```bash
# Show current configuration
browser-manager config

# Set resource limits
browser-manager config set max_tabs_per_agent 5
browser-manager config set max_browser_age_minutes 60
browser-manager config set max_memory_mb 1000

# Clear limits (back to unlimited)
browser-manager config clear

# Reset to factory defaults
browser-manager config reset
```

### Session Management

```bash
# Show browser session tracking data
browser-manager sessions

# Clean up session tracking data
browser-manager sessions cleanup

# Manual Finalization integration
browser-manager finalization-cleanup
```

## 📋 Usage Examples

### Basic Browser Management

```bash
# Check what browsers are running
/browser-manager status

# See detailed tab information
/browser-manager tabs

# Clean up your browsers when done
/browser-manager cleanup
```

### Cross-Agent Operations

```bash
# Clean up another agent's browsers (asks permission)
/browser-manager cleanup --agent agent-42

# Clean up all browsers across all agents (asks permission for each)
/browser-manager cleanup --all
```

### User Configuration

```bash
# Set limits to get warnings
/browser-manager config set max_tabs_per_agent 3
/browser-manager config set max_memory_mb 500

# Check if limits are exceeded
/browser-manager status
```

### Tab Management

```bash
# Show all tabs across all browsers
/browser-manager tabs --all-agents

# Close specific tabs (experimental)
/browser-manager close-tabs <pid> <tab-ids>
```

## 🔗 Integration Points

### Finalization Integration (Mandatory)

- **Automatic Cleanup**: `browser-manager finalization-cleanup` called by Finalization
- **Session Data Deletion**: Removes browser tracking at mission end
- **Resource Reporting**: Includes browser usage in Finalization summary

### UI Skill Integration

- **Pre-Test Tracking**: Track browsers before UI tests start
- **Post-Test Cleanup**: Clean up browsers after UI tests complete
- **Tab Counting**: Monitor tab usage during test execution

### Testing Skill Integration

- **Resource Warnings**: Show browser usage in test reports
- **Pre-Test Setup**: Ensure clean browser environment
- **Post-Test Cleanup**: Remove test browsers automatically

### Session Lock Integration

- **Agent Ownership**: Track which agent owns which browsers
- **Crash Recovery**: Handle orphaned browsers from crashed agents
- **Coordination**: Prevent browser conflicts between agents

## 📊 Metrics Tracked

- **Browser Processes**: PIDs, memory usage, start time, ownership
- **Tab Information**: URLs, titles, types, associated browsers
- **Agent Ownership**: Which agent owns which browsers/tabs
- **Resource Usage**: Memory consumption, process age, tab counts
- **Cleanup Actions**: Success/failure rates, cross-agent permissions

## 🎯 Key Features

### Tab-Level Tracking

- Uses Chrome DevTools Protocol to enumerate individual tabs
- Shows tab titles, URLs, and types
- Respects incognito mode (no tab inspection)
- Falls back to process analysis if DevTools unavailable

### Permission System

- Interactive terminal prompts for cross-agent cleanup
- Shows detailed browser/tab information before permission
- 30-second timeout with auto-cancel
- Audit logging of all cross-agent operations

### Configuration Without Defaults

- No resource limits by default (user must configure)
- Per-agent configuration support
- Persistent configuration across sessions
- Validation and warnings for restrictive settings

### Mission-End Cleanup

- Automatic session data deletion on Finalization
- Graceful browser shutdown with timeout
- Orphaned process detection and cleanup
- Audit trail before data deletion

## 🚨 Safety Features

### Soft Warnings Only

- Resource limits never block operations
- Warnings are informational only
- Can be suppressed by user configuration
- Always allows manual override

### Permission Protection

- Cross-agent cleanup requires explicit permission
- Detailed browser/tab information shown before action
- Audit logging for security and accountability
- Emergency force option with elevated warnings

### Privacy Respect

- Incognito mode tabs are not inspected
- URL/titles are truncated in status output
- Local URLs are filtered in summaries
- User data directories are respected

## 🛠️ Installation & Setup

### Dependencies

```bash
# Required Python packages
pip install psutil requests

# Optional for enhanced tab detection
pip install websocket-client
```

### Initial Setup

```bash
# Initial setup (creates config with no limits)
browser-manager config

# Set your preferred limits
/browser-manager config set max_tabs_per_agent 5
browser-manager config set max_memory_mb 1000
```

### Permissions

The skill needs permissions to:

- Access browser processes (psutil)
- Connect to Chrome DevTools (localhost ports)
- Read/write session tracking files
- Terminate browser processes (cleanup)

## 🔧 Troubleshooting

### Common Issues

**Tab detection not working:**

```bash
# Check if Chrome has remote debugging enabled
browser-manager status --debug

# Force refresh of browser detection
browser-manager status --refresh
```

**Permission denied errors:**

```bash
# Check browser process permissions
ps aux | grep chrome

# Run with elevated privileges if needed
sudo browser-manager cleanup --force
```

**Configuration issues:**

```bash
# Reset to factory defaults
browser-manager config reset

# Show current configuration
browser-manager config --verbose
```

### Debug Mode

```bash
# Enable debug logging
browser-manager status --debug

# Show detailed process information
browser-manager status --verbose --debug
```

## 📚 Configuration Reference

### Resource Limits

```yaml
limits:
  max_tabs_per_agent: null      # No limit by default
  max_browser_age_minutes: null # No time limit by default  
  max_memory_mb: null          # No memory limit by default
  max_browsers_total: null     # No global limit by default
```

### Admin Settings

```yaml
admin:
  require_permission_for_others: true
  permission_timeout_seconds: 30
  audit_log_enabled: true
  force_cleanup_confirmation: true
```

### Tracking Settings

```yaml
tracking:
  delete_on_mission_end: true
  session_retention_hours: 24
  tab_detection_timeout: 5
  process_scan_interval: 2
```

## 🎯 Best Practices

### Resource Management

1. **Configure limits** based on your system capabilities
2. **Monitor regularly** with `browser-manager status`
3. **Clean up frequently** after testing sessions
4. **Use Finalization integration** for automatic cleanup

### Multi-Agent Coordination

1. **Respect agent ownership** - don't cleanup others' browsers without permission
2. **Coordinate sessions** to avoid browser conflicts
3. **Use session locks** to prevent overlapping browser usage
4. **Communicate cleanup intentions** in agent messages

### Privacy & Security

1. **Review tab titles/URLs** before giving cleanup permission
2. **Use incognito mode** for sensitive testing
3. **Clear session data** after sensitive missions
4. **Monitor audit logs** for cross-agent activities

---

**Last Updated**: 2026-02-04  
**Part of**: LightRAG Skills Ecosystem  
**Version**: 1.0.0
