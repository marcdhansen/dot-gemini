---
name: skill-making
description: >
  Comprehensive guidelines and patterns for creating robust, reliable skills
  that work in both interactive and non-interactive (CI/CD) environments.
  Use when building a new skill, debugging EOF or non-interactive failures
  in an existing skill, or reviewing a skill's design for robustness.
  Do NOT use as a general Python or software design reference; this skill
  focuses specifically on skill authoring patterns for this ecosystem.
compatibility: >
  No external tools required for reading. The create_skill.py helper script
  lives at ~/.gemini/antigravity/skills/skill-making/create_skill.py.
metadata:
  author: Workshop Team
  version: "1.1.0"
  category: meta
  tags: [skill-authoring, patterns, non-interactive, robustness, testing]
---

# Skill: skill-making

# Skill-Making Skill

**Purpose**: Comprehensive guidelines and patterns for creating robust, reliable skills that work in both interactive and non-interactive environments.

Based on learnings from fixing EOF issues across the skill ecosystem and extensive experience with skill development, debugging, and maintenance.

## Usage

```bash
/skill-making
python ~/.gemini/antigravity/skills/skill-making/create_skill.py
```

## 🎯 Core Principles

### 1. Dual-Mode Design (CRITICAL)

**Every skill must work in both interactive and non-interactive environments from day 1.**

```python
import sys
import os

def is_non_interactive():
    """Standardized non-interactive detection"""
    return (
        not sys.stdin.isatty() or
        os.getenv("CI") or 
        os.getenv("GITHUB_ACTIONS") or
        os.getenv("AUTOMATED_MODE")
    )
```

### 2. Graceful Degradation

Never fail in non-interactive mode - always provide sensible fallbacks:

- ✅ **Input**: Auto-select defaults or read from stdin JSON
- ✅ **Prompts**: Skip or provide automated responses  
- ✅ **Timeouts**: Use reasonable defaults or skip
- ✅ **Errors**: Log and continue rather than crash

### 3. Environment-First Design

Design for CI/CD environments first, then enhance for interactive use:

- **Primary**: Non-interactive with sensible defaults
- **Secondary**: Interactive enhancements when terminal available
- **Testing**: Must work with `echo "" | skill` pattern

## 🏗️ Skill Structure Template

### **Required Files**

```
skill-name/
├── SKILL.md                    # Documentation and usage
├── scripts/
│   └── skill_name.py        # Main implementation
├── tests/
│   ├── test_skill_name.py      # Unit tests
│   └── integration_test.py     # Integration tests
├── config/
│   └── defaults.yaml          # Default configuration
└── README.md                   # Implementation details
```

### **SKILL.md Template**

```markdown
# Skill: skill-name

## Purpose
[One-sentence description]

## Usage
```bash
/skill-name
python skill_name.py [options]
```

## Implementation

- **Core Logic**: [Brief technical description]
- **Dependencies**: [List of required modules]
- **Environment Support**: Interactive + Non-interactive

## Error Handling

[Document error scenarios and recovery strategies]

## 🚨 Fixed Issues

[Document issues found and resolved during development]

## Integration

- **Finalization**: How it integrates with Finalization workflow
- **Initialization**: How it's used during Initialization phase
- **Skills**: Dependencies on other skills

## Testing

```bash
# Unit tests
python -m pytest tests/test_skill_name.py

# Integration tests
python -m pytest tests/integration_test.py

# Non-interactive testing
echo "" | python skill_name.py
```

```

## 🛠️ Development Patterns

### 1. Input Handling Pattern
```python
def safe_input(prompt, default=None, choices=None, fallback_func=None):
    """Robust input with comprehensive fallback"""
    if is_non_interactive():
        if fallback_func:
            return fallback_func()
        if choices:
            return choices[0]  # Default to first choice
        return default or "auto_generated"
    
    try:
        response = input(prompt).strip()
        
        # Validation
        if choices and response not in choices:
            print(f"⚠️ Invalid choice. Please select from: {choices}")
            return safe_input(prompt, default, choices, fallback_func)
        
        return response if response else default
    except (EOFError, KeyboardInterrupt):
        return default or "interrupted"
```

### 2. Configuration Pattern

```python
import yaml
from pathlib import Path

class SkillConfig:
    def __init__(self, config_path=None):
        self.config_path = config_path or Path(__file__).parent / "config" / "defaults.yaml"
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration with fallback defaults"""
        defaults = {
            "timeout": 30,
            "retry_count": 3,
            "auto_approve": False,
            "verbose": True
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    return {**defaults, **user_config}
            except Exception as e:
                print(f"⚠️ Config load failed: {e}, using defaults")
        
        return defaults
    
    def get(self, key, default=None):
        return self.config.get(key, default)
```

### 3. Error Recovery Pattern

```python
class SkillError(Exception):
    """Base skill exception with recovery information"""
    def __init__(self, message, recovery=None, retry=False):
        super().__init__(message)
        self.recovery = recovery
        self.retry = retry

def handle_skill_error(error, context=""):
    """Standardized error handling with recovery guidance"""
    print(f"❌ Skill Error: {error}")
    if error.recovery:
        print(f"🔧 Recovery: {error.recovery}")
    if error.retry:
        print(f"🔄 Retry recommended")
    
    # Log error for debugging
    import traceback
    traceback.print_exc()
```

### 4. Testing Pattern

```python
import unittest
import tempfile
import sys
from io import StringIO

class TestSkillNonInteractive(unittest.TestCase):
    """Test non-interactive functionality"""
    
    def test_non_interactive_detection(self):
        """Test CI environment detection"""
        # Mock non-interactive environment
        with patch('sys.stdin.isatty', return_value=False):
            self.assertTrue(is_non_interactive())
    
    def test_fallback_behavior(self):
        """Test graceful degradation"""
        # Simulate EOF conditions
        with patch('builtins.input', side_effect=EOFError):
            result = safe_input("test", default="fallback")
            self.assertEqual(result, "fallback")
    
    def test_stdin_json_parsing(self):
        """Test JSON stdin functionality"""
        test_data = '{"test": "data"}'
        with patch('sys.stdin.read', return_value=test_data):
            with patch('sys.stdin.isatty', return_value=False):
                # Test JSON parsing logic
                pass

if __name__ == "__main__":
    # Test with both interactive and non-interactive modes
    unittest.main()
```

## 🚫 Anti-Patterns to Avoid

### 1. Direct input() Calls

```python
# ❌ WRONG - Will fail in CI
response = input("Enter value: ")

# ✅ RIGHT - Robust with fallback
response = safe_input("Enter value: ", default="auto_value")
```

### 2. Missing EOF Handling

```python
# ❌ WRONG - Crashes in non-interactive environments
while True:
    choice = input("Select option: ")
    if choice in ["a", "b"]:
        break

# ✅ RIGHT - Handles EOF gracefully
while True:
    try:
        choice = safe_input("Select option: ", choices=["a", "b"])
        break
    except (EOFError, KeyboardInterrupt):
        print("🔄 Using default selection")
        choice = choices[0]
        break
```

### 3. Hardcoded Paths

```python
# ❌ WRONG - Assumes current directory
config_path = "./config.yaml"

# ✅ RIGHT - Uses script location
config_path = Path(__file__).parent / "config" / "defaults.yaml"
```

### 4. Missing Environment Detection

```python
# ❌ WRONG - Assumes interactive mode
print("Please enter your selection:")

# ✅ RIGHT - Adapts to environment
if is_non_interactive():
    print("🤖 Auto-selecting in non-interactive mode")
else:
    print("Please enter your selection:")
```

## 🔧 Skill Categories & Patterns

### 1. Finalization Skills (Critical)

**Purpose**: Called during Finalization workflow
**Requirements**: MUST be non-interactive compatible
**Examples**: playwright-manager, enhanced-reflection

**Critical Pattern**:

```python
def finalization_compatible_function():
    """Finalization skills must never block automated workflows"""
    if is_non_interactive():
        print("🤖 Non-interactive mode - Auto-approving")
        return True  # or auto-selected result
    
    # Interactive logic here
    return manual_result
```

### 2. Initialization Skills (Important)

**Purpose**: Called during Initialization phase
**Requirements**: Should work in CI environments
**Examples**: session-context, sop-checker

**Pattern**:

```python
def initialization_check():
    """Provide value regardless of environment"""
    data = gather_information()
    
    if is_non_interactive():
        print("📊 Pre-flight data gathered automatically")
    else:
        print("📊 Please review pre-flight data:")
        display_interactive(data)
    
    return data
```

### 3. Utility Skills (Flexible)

**Purpose**: General-purpose tools
**Requirements**: Adapt behavior based on environment
**Examples**: show-next-task, file-manager

**Pattern**:

```python
def utility_function():
    """Enhanced in interactive mode, functional in non-interactive"""
    result = core_logic()
    
    if not is_non_interactive():
        # Add interactive enhancements
        result = add_interactive_features(result)
    
    return result
```

## 🧪 Development Checklist

### ✅ Pre-Development

- [ ] **Define Purpose**: Clear single-responsibility principle
- [ ] **Identify Environment**: Will this be used in CI/CD?
- [ ] **Design Fallbacks**: What should happen automatically?
- [ ] **Plan Testing**: Unit + integration + non-interactive

### ✅ During Development

- [ ] **Use Standard Patterns**: Apply safe_input(), config handling
- [ ] **Test Non-Interactive**: `echo "" | skill.py` during development
- [ ] **Handle Exceptions**: Use SkillError with recovery info
- [ ] **Document Decisions**: Why this approach over alternatives?

### ✅ Post-Development

- [ ] **Unit Tests**: Test all functions and error cases
- [ ] **Integration Tests**: Test with real environment
- [ ] **Non-Interactive Tests**: Verify fallback behavior
- [ ] **Documentation**: Complete SKILL.md with examples
- [ ] **Examples**: Add usage examples for different modes

## 📚 Learning from Experience

### 🚨 Critical Lessons

1. **EOF Errors are Systemic**: If one skill has them, others probably do too
2. **Non-Interactive Detection**: Must use multiple checks (stdin + env vars)
3. **Fallback Behavior**: Must be sensible, not random defaults
4. **Testing Strategy**: `echo "" | skill` reveals all EOF issues immediately

### 🛠️ Technical Insights

1. **Input Validation**: Always validate user input and provide recovery guidance
2. **Configuration**: Use YAML for human-readable config with code defaults
3. **Error Messages**: Include recovery suggestions and next steps
4. **Logging**: Add structured logging for debugging non-interactive issues

### 🎯 Design Patterns

1. **Strategy Pattern**: Abstract interface, multiple implementations
2. **Factory Pattern**: Create appropriate handler based on environment
3. **Observer Pattern**: Log events for debugging without changing logic
4. **Command Pattern**: Encapsulate operations as undoable actions

### 🔄 Process Insights

1. **Develop Locally**: Use `./skill.py` for immediate testing
2. **Test in CI**: Push to test branch to verify CI behavior
3. **Iterate Quickly**: Fix issues as soon as they're discovered
4. **Document Continuously**: Update docs with each lesson learned

## 🔗 Integration Guidelines

### **Finalization Integration**

```bash
# In finalize.sh
if [ -f "$SKILL_PATH" ] && [ -x "$SKILL_PATH" ]; then
    "$SKILL_PATH" finalize-mode || echo "⚠️ Skill encountered issues"
fi
```

### **Skill Dependencies**

```python
# Import patterns for skill interdependencies
try:
    from other_skill import helper_function
except ImportError:
    print("⚠️ Dependent skill not available")
    print("🔧 Using fallback implementation")
    helper_function = fallback_implementation
```

### **Configuration Integration**

```yaml
# In ~/.gemini/antigravity/config/skills.yaml
skill_name:
  enabled: true
  timeout: 30
  auto_approve: false
  dependencies:
    - other_skill
    - utility_module
```

## 🎖️ Future-Proofing

### **Extensibility**

- **Plugin Architecture**: Design for easy extension and modification
- **Version Compatibility**: Maintain backward compatibility with skill interfaces
- **API Stability**: Keep public interfaces stable between versions

### **Maintainability**

- **Clear Separation**: Separate logic, configuration, and presentation
- **Comprehensive Tests**: Unit + integration + edge case coverage
- **Documentation**: Always update docs when changing behavior

### **Scalability**

- **Performance**: Consider resource usage for large-scale deployments
- **Concurrency**: Design for multi-agent environments if applicable
- **Monitoring**: Add metrics and health check capabilities

---

*Based on extensive experience fixing EOF issues and developing the skill ecosystem*

*Last Updated: 2026-02-05*
*Version: 1.1*
