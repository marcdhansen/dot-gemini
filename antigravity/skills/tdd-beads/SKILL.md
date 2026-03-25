---
name: tdd-beads
description: >
  Automatic beads issue creation with TDD compliance enforcement for feature
  development. Creates TDD-ready branches, worktrees, test templates, and
  documentation skeletons, then validates test-first commit ordering.
  Use when starting a new feature that requires both a beads issue and
  TDD scaffolding set up together.
  Do NOT use for general beads issue management (use beads-manager) or for
  non-TDD hotfix workflows.
compatibility: >
  Requires bd CLI, git, Python 3.x, and pytest. Scripts live in
  ~/.gemini/antigravity/skills/tdd-beads/scripts/.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: code-quality
  tags: [tdd, beads, issue-creation, compliance, feature-development]
  disable-model-invocation: true
  allowed-tools: Bash, Read, Edit, Glob, Grep
  dependencies: [planning, finalization, reflect]
---

# TDD-Beads Integration Skill

The `tdd-beads` skill provides automatic beads issue creation with mandatory TDD compliance enforcement for all feature development work. This skill ensures that every feature follows proper Test-Driven Development methodology from the very beginning.

## 🚀 Usage

```bash
# Automatic TDD-compliant task creation
/tdd-beads create <feature-name>     # Create beads issue with TDD requirements
/tdd-beads analyze <feature-name>    # Analyze feature for TDD requirements
/tdd-beads setup <feature-name>      # Setup complete TDD environment
/tdd-beads validate <feature-name>   # Validate TDD compliance before development

# Integrated workflow
/tdd-beads workflow <feature-name>   # Complete TDD setup workflow
/tdd-beads emergency <feature-name>   # Emergency TDD bypass (requires justification)
/tdd-beads retrospective             # Post-development TDD compliance check
```

## 🎯 Purpose

This skill implements **Mandatory TDD Integration** with three core capabilities:

### 1. **Automatic Beads Issue Creation** (TDD-First)

- **TDD-Ready Issues**: Automatically creates issues with TDD requirements
- **Branch Management**: Creates feature branches with TDD validation
- **Worktree Setup**: Isolated worktree for TDD development
- **Template Generation**: Creates TDD test files and documentation

### 2. **TDD Compliance Enforcement** (Quality Gates)

- **Pre-Development Validation**: Ensures all TDD artifacts exist before coding
- **Timeline Validation**: Validates test-first commit ordering
- **Quality Gate Integration**: Blocks non-compliant development
- **Automatic Reporting**: Generates TDD compliance reports

### 3. **Emergency & Fallback Procedures** (Safety Net)

- **Emergency Bypass**: Critical fixes with retrospective TDD
- **Gradual Compliance**: Phased TDD adoption for legacy code
- **Training Mode**: TDD learning mode with guidance
- **Compliance Recovery**: Fix TDD violations automatically

## 🏗️ Architecture

### Core Components

```
tdd-beads/
├── SKILL.md                     # This documentation
├── scripts/
│   ├── create_tdd_issue.py      # Main TDD issue creator
│   ├── tdd_compliance_validator.py # Compliance validation
│   ├── branch_manager.py        # Feature branch creation
│   ├── worktree_manager.py      # Isolated worktree setup
│   ├── template_generator.py    # TDD template generation
│   └── emergency_handler.py     # Emergency procedures
├── templates/
│   ├── tdd_test_template.py     # Failing test template
│   ├── functional_test_template.py # Functional test template
│   ├── tdd_documentation.md     # TDD documentation template
│   └── beads_issue_template.json # Beads issue template
├── config/
│   ├── tdd_config.yaml         # TDD configuration
│   ├── compliance_rules.yaml   # Compliance validation rules
│   └── emergency_procedures.yaml # Emergency configuration
├── integration/
│   ├── beads_integration.py     # Beads API integration
│   ├── git_integration.py       # Git workflow integration
│   ├── ci_integration.py         # CI/CD pipeline integration
│   └── skills_integration.py     # Other skill integrations
└── validation/
    ├── tdd_timeline_validator.py # Timeline validation
    ├── artifacts_validator.py    # Artifacts validation
    └── quality_gate_validator.py  # Quality gate validation
```

## 🔄 Workflow Integration

### Complete TDD Workflow

```bash
# 1. Feature Discovery
Agent: "I need to implement user authentication"
System: "🔍 Feature detected. Run `/tdd-beads create user-authentication`"

# 2. TDD Issue Creation
Agent: /tdd-beads create user-authentication
→ Creates beads issue with TDD requirements
→ Creates feature branch: feature/user-authentication
→ Creates isolated worktree
→ Generates TDD test templates
→ Sets up documentation skeleton

# 3. TDD Validation
Agent: /tdd-beads validate user-authentication
→ Validates all TDD artifacts exist
→ Checks branch and worktree setup
→ Validates beads issue configuration
→ Confirms test-first development ready

# 4. Development (with TDD gates)
→ Write failing tests (RED phase)
→ Run TDD compliance validation
→ Implement code to pass tests (GREEN phase)
→ Refactor while maintaining tests (REFACTOR phase)

# 5. Quality Gates
→ Automatic TDD timeline validation
→ Commit message validation (must reference beads issue)
→ Test coverage validation
→ Documentation completeness check
```

### Integration with Existing Systems

#### Orchestrator Integration

- **Post-Task-Selection**: Automatic TDD setup after task selection
- **Planning Integration**: TDD requirements included in planning phase
- **Progress Blocking**: TDD violations block further development

#### Initialization Enhancement

```bash
# Enhanced Initialization with TDD validation
✅ Environment ready (existing)
✅ TDD artifacts exist (new)
✅ Beads issue created (new)
✅ Feature branch active (new)
✅ Worktree isolated (new)
✅ Test timeline ready (new)
```

#### Finalization Integration

- **TDD Compliance Check**: Validates TDD requirements before session end
- **Automatic Fixes**: Fixes TDD violations when possible
- **Compliance Reports**: Generates TDD compliance documentation
- **Learning Capture**: Captures TDD lessons for improvement

## 📋 TDD Requirements Enforcement

### Mandatory TDD Artifacts

| Artifact | Purpose | Validation |
|----------|---------|------------|
| **Beads Issue** | Task tracking and requirements | Must exist and be active |
| **Feature Branch** | Isolated development | Cannot be main/master |
| **TDD Test File** | Failing tests first | Must fail initially |
| **Functional Tests** | Complete functionality | Must cover all requirements |
| **Documentation** | Analysis and tradeoffs | Must be comprehensive |
| **Worktree** | Isolated environment | Recommended for complex features |

### TDD Timeline Validation

```bash
# Required commit sequence
1. "test: create failing tests for user-authentication [lightrag-xxx]"
2. "feat: implement basic user-authentication to pass tests [lightrag-xxx]"
3. "refactor: improve user-authentication code quality [lightrag-xxx]"
4. "docs: complete user-authentication documentation [lightrag-xxx]"
```

### Quality Gate Integration

```bash
# Automated quality checks
✅ Test commits precede implementation commits
✅ Test files exist before implementation files
✅ Beads issue referenced in all commits
✅ Code coverage meets minimum thresholds
✅ Documentation is complete and accurate
✅ No TDD violations in git history
```

## 🚨 Emergency Procedures

### Critical Fix Bypass

```bash
# Emergency development (requires justification)
/tdd-beads emergency fix-production-bug --justification "Production system down"

→ Creates minimal beads issue
→ Enables emergency branch (emergency/fix-production-bug)
→ Bypasses TDD template requirements
→ Schedules retrospective TDD compliance
→ Requires admin approval
```

### Retrospective TDD

```bash
# Fix TDD violations after development
/tdd-beads retrospective --task completed-feature

→ Analyzes git history for TDD violations
→ Creates missing TDD artifacts
• Generates tests based on implementation
• Creates documentation from code
• Updates beads issue with TDD information
• Generates compliance report
```

### Gradual Compliance

```bash
# Legacy code TDD adoption
/tdd-beads gradual --module legacy-component

→ Analyzes current code coverage
• Identifies test gaps
• Prioritizes critical paths
• Creates incremental TDD plan
• Sets up monitoring for compliance
```

## 🔗 Beads Integration

### Automatic Issue Creation

```json
{
  "title": "Feature: user-authentication (TDD-Compliant)",
  "priority": "P0",
  "type": "feature",
  "tags": ["tdd", "feature", "authentication"],
  "description": "Implementation of user authentication with full TDD compliance",
  "tdd_requirements": {
    "test_files": ["tests/user_authentication_tdd.py"],
    "functional_tests": ["tests/user_authentication_functional.py"],
    "documentation": ["docs/user_authentication_analysis.md"],
    "branch": "feature/user-authentication",
    "timeline": "test_first_development"
  },
  "checklist": [
    "Create failing tests (RED)",
    "Implement basic functionality (GREEN)",
    "Add comprehensive functional tests",
    "Complete documentation and analysis",
    "Validate TDD timeline compliance"
  ]
}
```

### Task Management Integration

```bash
# Automatic task creation for complex features
/tdd-beads create complex-feature --breakdown

→ Creates main feature task
• Creates sub-tasks for TDD phases
• Sets up dependencies
• Creates milestone structure
• Configures automated reporting
```

## 📊 Success Metrics

### P0 Success Criteria

- **100%** Beads issue creation before feature development
- **100%** Feature branch usage for development
- **100%** TDD test file creation before implementation
- **100%** Test-first commit timeline validation
- **<2 minutes** TDD setup time per feature
- **>95%** TDD compliance rate across all features

### Quality Metrics

- **Setup Time**: Average time to create TDD environment
- **Compliance Rate**: Percentage of features following TDD
- **Test Coverage**: Code coverage with TDD vs. without
- **Bug Reduction**: Bug rate reduction with TDD adoption
- **Developer Satisfaction**: Developer experience with TDD workflow

## 🔧 Configuration

### Main Configuration

```yaml
# config/tdd_config.yaml
tdd_beads:
  auto_create_issues: true
  enforce_branch_protection: true
  require_worktree_isolation: false
  timeline_validation: strict
  
templates:
  test_framework: "pytest"
  documentation_format: "markdown"
  commit_message_format: "conventional"
  
compliance:
  minimum_test_coverage: 80
  require_functional_tests: true
  require_documentation: true
  enforce_timeline: true
  
emergency:
  allow_bypass: true
  require_justification: true
  admin_approval_required: true
  retrospective_required: true
```

### Integration Configuration

```yaml
# integration/skills_integration.yaml
skills:
  planning:
    include_tdd_requirements: true
    auto_create_tdd_tasks: false
    
  return_to_base:
    tdd_compliance_check: mandatory
    auto_fix_violations: true
    
  orchestrator:
    prompt_tdd_setup: true
    block_non_compliant: true
    
  reflect:
    capture_tdd_lessons: true
    suggest_improvements: true
```

## 📚 Examples & Use Cases

### Example 1: Standard Feature Development

```bash
# Agent wants to implement user authentication
Agent: "I need to add user authentication to the system"

System: "🔍 Feature detected. Use TDD-compliant development:"
System: "Run: /tdd-beads create user-authentication"

Agent: /tdd-beads create user-authentication

✅ Created beads issue lightrag-xyz
✅ Created feature branch feature/user-authentication
✅ Created isolated worktree
✅ Generated TDD test template: tests/user_authentication_tdd.py
✅ Generated functional test template: tests/user_authentication_functional.py
✅ Created documentation skeleton: docs/user_authentication_analysis.md

System: "🚀 TDD environment ready. Start with failing tests:"
System: "1. Edit tests/user_authentication_tdd.py"
System: "2. Run: pytest tests/user_authentication_tdd.py (should fail)"
System: "3. Implement code to pass tests"
```

### Example 2: Emergency Fix

```bash
# Production issue requires immediate fix
Agent: "Production is down due to authentication failure"
Agent: "/tdd-beads emergency fix-auth-bug --justification 'Production down'"

⚠️ EMERGENCY MODE ACTIVATED
✅ Created emergency beads issue lightrag-emergency-123
✅ Created emergency branch emergency/fix-auth-bug
✅ Enabled immediate development
⚠️ Retrospective TDD compliance scheduled
⚠️ Admin approval required

System: "Emergency development enabled. Fix the issue now."
System: "TDD compliance will be addressed retrospectively."
```

### Example 3: Legacy Code Adoption

```bash
# Add TDD to existing codebase
Agent: "/tdd-beads gradual --module payment-processor"

📊 Analyzing legacy module...
✅ Current test coverage: 15%
✅ Critical paths identified: 8
✅ TDD adoption plan created
✅ Incremental milestones defined

System: "Gradual TDD adoption plan ready:"
System: "1. Create tests for critical payment flow"
System: "2. Add tests for error handling"
System: "3. Cover edge cases and validation"
System: "4. Complete documentation"
System: "5. Monitor compliance"
```

## 🆘 Troubleshooting

### Common Issues

**Beads Issue Creation Fails**:

```bash
# Check beads daemon
bd status
bd daemon start

# Verify repository
bd init
```

**Branch Protection Errors**:

```bash
# Check current branch
git branch --show-current

# Create feature branch
git checkout -b feature/your-feature
```

**TDD Template Issues**:

```bash
# Regenerate templates
/tdd-beads setup your-feature --force
```

**Timeline Validation Fails**:

```bash
# Check commit history
git log --oneline

# Fix commit ordering
git rebase -i HEAD~5
```

### Getting Help

```bash
# TDD-Beads help
/tdd-beads help                    # General help
/tdd-beads help create            # Issue creation help
/tdd-beads help emergency         # Emergency procedures help
/tdd-beads help compliance        # Compliance validation help
```

---

**Status**: P0 Critical Infrastructure  
**Version**: 1.0.0  
**Last Updated**: 2026-02-05  
**Integration**: Beads, Planning, Orchestrator, Finalization, Reflect  

For issues or improvements, create a beads task with `tdd-beads` tag.
