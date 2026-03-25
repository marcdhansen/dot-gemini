# Browser Manager Skill - User Guide

## 🚀 Quick Start

The Browser Manager skill helps manage Playwright browser processes to prevent resource leaks during automated testing.

### Installation

The skill is automatically available through the LightRAG skills ecosystem. No additional installation required.

### Basic Usage

```bash
# Check current browser usage
browser-manager status

# Clean up your browsers
browser-manager cleanup

# Show detailed tab information  
browser-manager tabs

# Configure limits
browser-manager config set max_tabs_per_agent 5
```

## 📋 Common Workflows

### 1. Before UI Testing

```bash
# Check current browser state
browser-manager status

# Set limits if desired
browser-manager config set max_memory_mb 1000

# Run your UI tests
# ... your test commands here ...

# Clean up after testing
browser-manager cleanup
```

### 2. Resource Management

```bash
# Check if you're approaching limits
browser-manager check-limits

# Get detailed view of all tabs
browser-manager tabs --verbose

# Clean up if needed
browser-manager cleanup
```

### 3. Multi-Agent Coordination

```bash
# Clean up another agent's browsers (asks permission)
browser-manager cleanup --agent agent-42

# Clean up all browsers across all agents
browser-manager cleanup --all
```

## 🛠️ Configuration

### Setting Limits

```bash
# Limit tabs per agent
browser-manager config set max_tabs_per_agent 5

# Limit memory usage per agent
browser-manager config set max_memory_mb 500

# Limit browser age
browser-manager config set max_browser_age_minutes 30

# View current limits
browser-manager config
```

### Removing Limits

```bash
# Remove all limits (back to unlimited)
browser-manager config clear

# Reset to factory defaults
browser-manager config reset
```

## 📊 Understanding the Output

### Status Output

```text
🌐 Browser Manager Status - Agent: marchansen
==================================================

📊 Global Stats:
  • Total agents: 2
  • Total browsers: 3
  • Total tabs: 12
  • Total memory: 450MB

🖥️  Your Browser Sessions:
  • Browsers: 1
  • Tabs: 5
  • Memory: 150MB
```

### Tab Details

```text
📄 All Browser Tabs:

📍 PID 1234 (marchansen): 5 tabs
  📄 LightRAG Knowledge Graph
     http://localhost:5173/knowledge-graph
  📄 Retrieval Testing
     http://localhost:5173/retrieval
  📄 GitHub - Pull Request
     https://github.com/user/repo/pull/42
  📄 New Tab
     chrome://newtab/
  📄 Chrome Settings
     chrome://settings/
```

## ⚠️ Resource Warnings

When limits are exceeded, you'll see warnings:

```text
⚠️ Resource Warnings:
  • High tab count: 8 >= 5
  • High memory usage: 1200MB >= 1000MB
  • Old browser: PID 1234 running for 2:15:30
```

## 🔧 Advanced Usage

### Detailed Status

```bash
# Show detailed browser and tab information
browser-manager status --detailed
```

### Session Tracking

```bash
# View browser session tracking data
browser-manager sessions

# Clean up session data
browser-manager sessions cleanup
```

### Verbose Output

```bash
# Enable verbose debugging
browser-manager status --verbose
browser-manager tabs --verbose
```

## 🛡️ Safety Features

### Permission System

When cleaning other agents' browsers, you'll see detailed information and be asked for permission:

```text
🔒 Admin Permission Required
Attempting to clean up 2 browser(s) from agent 'agent-42'

  • PID 5678: 3 tabs, 200MB, running 1:45:20
    - LightRAG UI Testing
    - GitHub Repository
    - Documentation Page

Clean up agent-42's 2 browser(s) with 3 tabs? [y/N] 
```

### Audit Logging

All cross-agent cleanup operations are logged to `~/.gemini/browser_audit.log` for security.

### Graceful Shutdown

Browsers are shut down gracefully first, then force-killed if needed after a timeout.

## 🔍 Troubleshooting

### Tab Detection Not Working

```bash
# Check if Chrome has remote debugging enabled
browser-manager status --debug

# Force refresh browser detection
browser-manager status --refresh
```

### Permission Errors

```bash
# Use force mode (not recommended for other agents)
browser-manager cleanup --force
```

### Configuration Issues

```bash
# Reset configuration
browser-manager config reset

# Check current config
browser-manager config --verbose
```

## 🔄 Finalization Integration

The skill integrates automatically with Finalization:

```bash
# Finalization calls this automatically
browser-manager finalization-cleanup
```

This:

1. Cleans up your browsers
2. Deletes session tracking data  
3. Reports cleanup summary

## 📝 Best Practices

### 1. Set Appropriate Limits

Configure limits based on your system resources:

```bash
browser-manager config set max_memory_mb 1000    # 1GB per agent
browser-manager config set max_tabs_per_agent 5     # 5 tabs per agent
```

### 2. Clean Up Regularly

Clean up browsers after testing sessions:

```bash
# After UI tests
browser-manager cleanup

# After manual browser usage  
browser-manager status
# Check if cleanup needed
```

### 3. Monitor Resource Usage

Check limits regularly:

```bash
# In your workflow
browser-manager check-limits || echo "Consider cleanup"
```

### 4. Use Finalization Integration

Let Finalization handle automatic cleanup at mission end.

### 5. Respect Agent Ownership

Always ask permission before cleaning other agents' browsers.

## 🔗 Integration Examples

### UI Skill Integration

```bash
# Before tests
browser-manager track-browsers --before-test

# After tests
browser-manager cleanup --agent-only
```

### Testing Skill Integration  

```bash
# Add to test scripts
browser-manager check-limits
if [ $? -ne 0 ]; then
    echo "⚠️ High browser usage detected"
fi
```

### Session Lock Integration

```bash
# Agent start
browser-manager track-session $AGENT_ID

# Agent end  
browser-manager cleanup --agent $AGENT_ID
```

---

For more help, run `browser-manager --help` or see the main skill documentation.
