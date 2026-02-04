#!/usr/bin/env python3
"""
Skill Creation Assistant
Automated skill creation based on skill-making best practices and patterns
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


class SkillCreator:
    def __init__(self):
        self.templates_dir = Path(__file__).parent
        self.skills_root = Path.home() / ".gemini" / "antigravity" / "skills"

    def create_skill(self, name: str, description: str, category: str = "utility"):
        """Create a new skill with all required files and structure"""

        skill_name = name.lower().replace(" ", "_").replace("-", "_")
        skill_dir = self.skills_root / skill_name

        print(f"🔧 Creating skill: {skill_name}")
        print(f"📍 Location: {skill_dir}")
        print(f"📝 Description: {description}")
        print(f"🏷️ Category: {category}")
        print()

        # Create directory structure
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "scripts").mkdir(exist_ok=True)
        (skill_dir / "tests").mkdir(exist_ok=True)
        (skill_dir / "config").mkdir(exist_ok=True)

        # Create files
        self._create_skill_md(skill_dir, skill_name, name, description, category)
        self._create_main_script(skill_dir, skill_name, name, description)
        self._create_tests(skill_dir, skill_name)
        self._create_config(skill_dir, skill_name)
        self._create_readme(skill_dir, skill_name, description)

        print(f"✅ Skill '{skill_name}' created successfully!")
        print()
        print("📋 Next Steps:")
        print(f"1. cd {skill_dir}")
        print(f"2. Edit scripts/{skill_name}.py")
        print("3. Run tests: python -m pytest tests/")
        print("4. Test non-interactive: echo '' | python scripts/{skill_name}.py")
        print()
        print("🛠️  Remember to apply skill-making patterns:")
        print("- Use safe_input() for user interactions")
        print("- Add is_non_interactive() checks")
        print("- Provide fallback behaviors")
        print("- Handle EOFError/KeyboardInterrupt gracefully")

    def _create_skill_md(
        self,
        skill_dir: Path,
        skill_name: str,
        display_name: str,
        description: str,
        category: str,
    ):
        """Create SKILL.md file with comprehensive documentation"""

        content = f"""# Skill: {skill_name}

# {display_name.title()}

{description}

## Usage

```bash
/skill-name
python {skill_name}.py [options]
```

## Implementation

- **Core Logic**: [Brief technical description]
- **Dependencies**: [List of required modules]
- **Environment Support**: Interactive + Non-interactive

## Error Handling

[Document error scenarios and recovery strategies]

## 🚨 Fixed Issues

[Document issues found and resolved during development - use template from skill-making SKILL.md]

## Integration

- **RTB**: How it integrates with Return To Base workflow
- **PFC**: How it's used during Pre-Flight Check
- **Skills**: Dependencies on other skills

## Testing

```bash
# Unit tests
python -m pytest tests/test_{skill_name}.py

# Integration tests
python -m pytest tests/integration_test.py

# Non-interactive testing
echo "" | python scripts/{skill_name}.py
```

---

*Based on skill-making best practices from skill-making skill*
*Last Updated: {datetime.now().strftime("%Y-%m-%d")}*
"""

        with open(skill_dir / "SKILL.md", "w") as f:
            f.write(content)

    def _create_main_script(
        self, skill_dir: Path, skill_name: str, display_name: str, description: str
    ):
        """Create main script with robust patterns"""

        class_name = display_name.title().replace(" ", "").replace("-", "")

        content = f'''#!/usr/bin/env python3
"""
{display_name} - {description}

Robust skill implementation following skill-making best practices.
Supports both interactive and non-interactive environments.
"""

import sys
import os
import argparse
from pathlib import Path


def is_non_interactive():
    """Standardized non-interactive detection"""
    return (
        not sys.stdin.isatty() or
        os.getenv("CI") or 
        os.getenv("GITHUB_ACTIONS") or
        os.getenv("AUTOMATED_MODE")
    )


def safe_input(prompt, default=None, choices=None, fallback_func=None):
    """Safe input with non-interactive fallback"""
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
            print(f"⚠️  Invalid choice. Please select from: {{choices}}")
            return safe_input(prompt, default, choices, fallback_func)
        
        return response if response else default
    except (EOFError, KeyboardInterrupt):
        return default or "interrupted"


class {class_name}:
    """Main skill class with robust error handling"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or Path(__file__).parent / "config" / "defaults.yaml"
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration with fallback defaults"""
        defaults = {{
            "timeout": 30,
            "retry_count": 3,
            "auto_approve": False,
            "verbose": True
        }}
        
        if self.config_path.exists():
            try:
                import yaml
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    return {{**defaults, **user_config}}
            except Exception as e:
                print(f"⚠️  Config load failed: {{e}}, using defaults")
        
        return defaults
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def main(self):
        """Main skill execution"""
        parser = argparse.ArgumentParser(
            description="{description}",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            "--non-interactive", 
            action="store_true",
            help="Run in non-interactive mode"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        args = parser.parse_args()
        
        try:
            self._execute_skill(args)
        except KeyboardInterrupt:
            print("\\n👋 Skill interrupted")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Skill failed: {{e}}")
            sys.exit(1)
    
    def _execute_skill(self, args):
        """Execute core skill logic"""
        print(f"🔧 Executing {skill_name}...")
        
        if is_non_interactive():
            print("🤖 Non-interactive mode detected")
            # Add your non-interactive logic here
            result = self._non_interactive_logic(args)
        else:
            print("📝 Interactive mode")
            # Add your interactive logic here
            result = self._interactive_logic(args)
        
        print(f"✅ {skill_name} completed successfully!")
        return result
    
    def _non_interactive_logic(self, args):
        """Logic for non-interactive environments"""
        # Implement your skill's automatic behavior here
        print("🔄 Running automated logic...")
        # Example: auto-select defaults, use environment variables, etc.
        return "auto_result"
    
    def _interactive_logic(self, args):
        """Logic for interactive environments"""
        # Implement your skill's interactive behavior here
        print("📋 Running interactive logic...")
        # Example: prompt user for input, show options, etc.
        return "interactive_result"


def main():
    """Entry point"""
    skill = {class_name}()
    
    # Check if being imported as module
    if len(sys.argv) == 1:
        skill.main()
    else:
        # Being called with arguments
        skill.main()


if __name__ == "__main__":
    main()
'''

        with open(skill_dir / "scripts" / f"{skill_name}.py", "w") as f:
            f.write(content)

        # Make executable
        os.chmod(skill_dir / "scripts" / f"{skill_name}.py", 0o755)

    def _create_tests(self, skill_dir: Path, skill_name: str):
        """Create test files"""

        # Unit tests
        unit_test_content = f'''import unittest
import sys
from io import StringIO
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(skill_dir.parent))

from scripts.{skill_name} import {skill_name.title().replace("_", "")}


class Test{skill_name.title().replace("_", "")}NonInteractive(unittest.TestCase):
    """Test non-interactive functionality"""
    
    def test_non_interactive_detection(self):
        """Test CI environment detection"""
        with patch('sys.stdin.isatty', return_value=False):
            # Import here to test the function
            from scripts.{skill_name} import is_non_interactive
            self.assertTrue(is_non_interactive())
    
    def test_fallback_behavior(self):
        """Test graceful degradation"""
        # Mock non-interactive environment and test fallback
        with patch('sys.stdin.isatty', return_value=False):
            # Test safe_input with fallback
            pass  # Add your specific tests here
    
    def test_stdin_json_parsing(self):
        """Test JSON stdin functionality"""
        test_data = '{{"test": "data"}}'
        with patch('sys.stdin.read', return_value=test_data):
            with patch('sys.stdin.isatty', return_value=False):
                # Test JSON parsing logic
                pass  # Add your specific tests here


if __name__ == "__main__":
    # Test with both interactive and non-interactive modes
    unittest.main()
'''

        with open(skill_dir / "tests" / f"test_{skill_name}.py", "w") as f:
            f.write(unit_test_content)

        # Integration test template
        integration_test_content = f'''import subprocess
import sys
import tempfile
from pathlib import Path


def test_{skill_name}_integration():
    """Integration test for {skill_name}"""
    print(f"🧪 Testing {skill_name} integration...")
    
    try:
        # Test basic functionality
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "scripts" / "{skill_name}.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Basic functionality test passed")
        else:
            print(f"❌ Help command failed: {{result.stderr}}")
        
        # Test non-interactive mode
        result = subprocess.run(
            ['bash', '-c', f'echo "" | python (Path(__file__).parent.parent / "scripts" / "{skill_name}.py")'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Non-interactive test passed")
        else:
            print(f"❌ Non-interactive test failed: {{result.stderr}}")
            
    except Exception as e:
        print(f"❌ Integration test failed: {{e}}")
        return False
    
    if __name__ == "__main__":
        test_{skill_name}_integration()
'''

        with open(skill_dir / "tests" / "integration_test.py", "w") as f:
            f.write(integration_test_content)

    def _create_config(self, skill_dir: Path, skill_name: str):
        """Create default configuration file"""

        config_content = f"""# {skill_name} Default Configuration

# Timeout settings
timeout: 30
retry_count: 3

# Behavior settings
auto_approve: false
verbose: true

# Example environment-specific settings
development:
  timeout: 60
  verbose: true

production:
  timeout: 120
  auto_approve: true
  verbose: false
"""

        with open(skill_dir / "config" / "defaults.yaml", "w") as f:
            f.write(config_content)

    def _create_readme(self, skill_dir: Path, skill_name: str, description: str):
        """Create README file with implementation details"""

        readme_content = f"""# {skill_name.title().replace("_", " ")} Skill

{description}

## 📁 Files Created

- `SKILL.md` - Skill documentation and usage
- `scripts/{skill_name}.py` - Main implementation with robust patterns
- `tests/test_{skill_name}.py` - Unit tests
- `tests/integration_test.py` - Integration tests
- `config/defaults.yaml` - Default configuration

## 🚀 Quick Start

### Installation
```bash
# Skill is automatically available in global skills path
/skill-name
```

### Usage Examples

```bash
# Interactive mode
/skill-name

# Non-interactive mode (CI/CD)
/skill-name --non-interactive

# With custom config
/skill-name --config /path/to/config.yaml
```

### Configuration

See `config/defaults.yaml` for all available options.

Environment-specific configuration can be added to override defaults.

## 🔧 Development

### Testing
```bash
# Run unit tests
python -m pytest tests/test_{skill_name}.py

# Run integration tests
python tests/integration_test.py

# Test non-interactive behavior
echo "" | python scripts/{skill_name}.py
```

### Skill-Making Patterns Applied

- ✅ **Non-Interactive Detection**: `is_non_interactive()` function
- ✅ **Safe Input**: `safe_input()` with fallback support
- ✅ **Error Handling**: Graceful degradation and recovery
- ✅ **Configuration**: YAML-based with code defaults
- ✅ **Testing**: Unit + integration + non-interactive tests

## 🔗 Integration

### RTB Integration
Add to return-to-base.sh:
```bash
if [ -f "$SKILL_PATH" ] && [ -x "$SKILL_PATH" ]; then
    "$SKILL_PATH" rtb-mode || echo "⚠️ Skill encountered issues"
fi
```

### PFC Integration
Call during Pre-Flight Check for validation or data gathering.

## 📚 Dependencies

- `pyyaml` - Configuration parsing
- `argparse` - Command line argument handling

## 🛠️ Troubleshooting

### Common Issues
- **EOF Errors**: Fixed by non-interactive detection
- **Permission Errors**: Check executable permissions
- **Import Errors**: Verify Python path and dependencies

### Debug Mode
```bash
/skill-name --verbose
```

---

*Created using skill-making skill with best practices*
*Last Updated: {datetime.now().strftime("%Y-%m-%d")}*
"""

        with open(skill_dir / "README.md", "w") as f:
            f.write(readme_content)


def main():
    """Main entry point for skill creation"""
    parser = argparse.ArgumentParser(
        description="Create new skill with best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("name", help="Skill name (e.g., 'data-processor')")
    parser.add_argument("description", help="Brief description of skill purpose")
    parser.add_argument(
        "--category",
        default="utility",
        choices=["utility", "rtb", "pfc", "planning", "analysis"],
        help="Skill category (default: utility)",
    )

    args = parser.parse_args()

    try:
        creator = SkillCreator()
        creator.create_skill(args.name, args.description, args.category)
    except KeyboardInterrupt:
        print("\n👋 Skill creation cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Skill creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
