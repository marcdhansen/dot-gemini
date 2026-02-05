---
name: planning
description: Comprehensive planning skill with blast radius analysis, incremental validation, and value-driven change management for LightRAG features and tasks
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
version: "1.0.0"
dependencies: [show-next-task, return-to-base, reflect]
---

# Planning Skill - P0 Critical Infrastructure

The `planning` skill provides comprehensive planning capabilities for the LightRAG project, featuring blast radius analysis, incremental validation, and value-driven change management. This is a **P0 critical infrastructure** skill that ensures systematic, safe, and measurable feature development.

## 🚀 Usage

```bash
# Primary workflow (Orchestrator integration)
/plan scope <task-id>       # Scope selected task with blast radius analysis
/plan analyze <task-id>     # Detailed analysis and recommendations
/plan proceed <task-id>     # Create implementation plan and milestones
/plan table <task-id>       # Save scoping information, return to task selection

# Direct planning commands
/plan create <feature-name> # Create new feature plan from scratch
/plan validate <plan-id>    # Validate and approve existing plan
/plan track <plan-id>       # Track progress and milestones
/plan rollback <feature>    # Execute rollback procedures

# Analysis commands
/plan blast-radius <path>   # Quick blast radius analysis
/plan dependencies <target> # Dependency analysis for component
/plan impact <change>      # Comprehensive impact assessment
```

## 🎯 Purpose

This skill implements an **Integrated Planning System** with three core capabilities:

### 1. **Blast Radius Analysis** (Progressive Disclosure)

- **Level 1: Summary** - Quick overview with risk assessment
- **Level 2: Detailed** - Module-level analysis with dependencies
- **Level 3: Deep-Dive** - Complete architectural impact analysis

### 2. **Incremental Validation System** (Hybrid Approach)

- **Milestone-Based Validation** - Success criteria at each development phase
- **A/B Testing Framework** - Statistical significance testing
- **Rollback-Safe Deployment** - User-controlled rollback triggers

### 3. **Task Planning & Integration** (Orchestrator Integration)

- **Post-Task-Selection Planning** - Automatic scoping prompt after task selection
- **Beads Integration** - Recommend and create tasks after user approval
- **Progress Blocking** - Failed milestones automatically block further progress

## 🏗️ Architecture

### Core Components

```text
planning/
├── SKILL.md                    # This documentation
├── scripts/
│   ├── create_plan.sh          # Main planning orchestrator
│   ├── blast_radius_analyzer.py # Progressive disclosure analysis
│   ├── incremental_validator.py # Value-driven change validation
│   ├── milestone_tracker.py   # Milestone-based progress tracking
│   ├── risk_assessor.py       # Multi-dimensional risk analysis
│   └── orchestrator_integration.py # Orchestrator interface
├── templates/
│   ├── feature_plan.md        # Feature planning template
│   ├── task_scope.md          # Task scoping template
│   ├── blast_radius_report.md # Impact assessment template
│   └── incremental_plan.md    # Incremental change template
├── config/
│   ├── planning_config.yaml   # Main configuration
│   ├── blast_radius_rules.yaml # Analysis rules and thresholds
│   ├── milestone_criteria.yaml # Success criteria definitions
│   └── orchestrator_config.yaml # Integration configuration
├── integration/
│   ├── beads_integration.py   # Task management integration
│   ├── tdd_gate_enhancement.py # Quality gate integration
│   ├── git_workflow.py         # Git workflow integration
│   └── api_endpoints.py        # LightRAG API integration
├── models/
│   ├── planning_models.py     # Pydantic models for planning data
│   └── validation_models.py   # Validation result models
└── utils/
    ├── graph_utils.py         # Dependency graph algorithms
    ├── file_utils.py          # File processing utilities
    └── metrics_utils.py       # Metrics calculation utilities
```

## 🔄 Workflow Integration

### Orchestrator Integration

The planning skill integrates seamlessly with the **Orchestrator** system to provide **post-task-selection planning**:

1. **Task Selection**: Agent selects task using `/next` command
2. **Orchestrator Prompt**: Automatically prompts for planning scoping
3. **Planning Mode**: Agent runs `/plan scope <task-id>` to analyze task
4. **Decision Point**: Agent chooses to proceed with development or table task
5. **Plan Creation**: If proceeding, create implementation plan with milestones

### Enhanced Initialization

The skill enhances the existing Initialization system with planning validation:

```bash
# Enhanced Initialization checks
✅ Basic readiness (existing)
✅ Planning scope completed (new)
✅ Milestones defined (new)
✅ Blast radius analyzed (new)
✅ Rollback procedures validated (new)
```

## 📊 Blast Radius Analysis

### Progressive Disclosure Levels

#### **Level 1: Summary Analysis** (Quick Overview)

- Affected files count and critical paths
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Estimated testing effort and deployment impact
- Timeline impact and resource requirements

#### **Level 2: Detailed Analysis** (Development Planning)

- File impacts with specific changes required
- Dependency chain analysis and test coverage gaps
- Migration requirements and rollback complexity
- Integration points affected and cross-module dependencies

#### **Level 3: Deep-Dive Analysis** (Architecture Review)

- Performance implications and security considerations
- Long-term maintenance impact and technical debt analysis
- Cross-system integration effects and compliance requirements
- Documentation and training requirements

### Analysis Dimensions

| Dimension | Metrics | Impact Level |
| :--- | :--- | :--- |
| **Code** | Files changed, functions modified, API changes | HIGH |
| **Configuration** | Schema changes, environment impacts, security settings | MEDIUM |
| **Database** | Schema migrations, data transformations, index changes | CRITICAL |
| **Documentation** | Updates required, examples affected, API docs | LOW |
| **Testing** | New tests needed, coverage gaps, integration tests | HIGH |

## 🚦 Incremental Validation System

### Milestone-Based Workflow

```bash
# Development Milestones
1. Development Phase       → Unit Tests + Code Coverage
2. Integration Phase       → Integration Tests + API Compatibility  
3. A/B Testing Phase      → Statistical Significance + Performance
4. Production Readiness   → Security Scan + Rollback Validation
5. Production Deployment  → Health Checks + Monitoring Validation
```

### Validation Blocking

- **Failed Milestones Block Progress**: Cannot proceed to next phase
- **Adaptive Thresholds**: Success criteria adjust based on complexity
- **Emergency Bypass**: User approval required with justification
- **Automatic Rollback**: Triggered on critical validation failures

### A/B Testing Integration

- **Statistical Significance**: T-tests, Z-tests, Chi-square analysis
- **Effect Size Measurement**: Cohen's d, correlation coefficients
- **Sample Size Calculation**: Power analysis for minimum detectable effect
- **Decision Rules**: Automated go/no-go based on statistical criteria

## 🔗 System Integration

### Beads Task Management

```bash
# Task Recommendation Workflow
1. Blast radius analysis → Identify impact areas
2. Risk assessment → Determine task complexity  
3. Recommend tasks → Present to user for approval
4. Create tasks → User approval triggers task creation
5. Link dependencies → Automatic dependency management
```

### Quality Gate Integration

- **Enhanced TDD Gates**: Planning-specific test requirements
- **Coverage Analysis**: Dependency coverage validation
- **Quality Metrics**: Planning-based quality assessment
- **Compliance Checking**: Automated compliance validation

### Git Workflow Integration

- **Branch Protection**: Planning validation before branch creation
- **Commit Validation**: Automatic blast radius checking
- **PR Integration**: Planning status in pull requests
- **Tag Management**: Milestone-based release tagging

## 🛡️ Safety & Fallback Mechanisms

### Fallback Strategy

The planning skill uses a **Fallback Mechanism** approach:

- **Primary System**: New planning skill as default
- **Fallback Options**: Manual planning, beads-only, direct development
- **Emergency Procedures**: Critical fix bypass with retrospective planning
- **Gradual Migration**: Coexistence period with existing processes

### Conflict Resolution

```python
# Conflict Scenarios & Resolutions
Existing Manual Plan → Merge with planning skill analysis
Beads Task Only → Enhance with blast radius analysis
Emergency Development → Minimal planning + retrospective analysis
Legacy Process Conflict → Configurable preference system
```

### Safety Mechanisms

- **Pre-Deployment Validation**: Rollback procedures verified before deployment
- **Circuit Breakers**: Automatic stop on repeated failures
- **Emergency Rollback**: User-triggered immediate rollback
- **Audit Trail**: Complete logging of all planning decisions

## 📈 Success Metrics

### P0 Success Criteria

- **100%** Orchestrator planning prompt compliance
- **100%** Blast radius analysis for P0/P1 tasks  
- **100%** Milestone blocking enforcement
- **100%** Rollback capability verification
- **<5 minutes** Planning scoping time per task
- **>90%** User satisfaction with planning workflow

### Quality Metrics

- **Planning Time**: Average time to scope and plan tasks
- **Accuracy Rate**: Blast radius prediction accuracy
- **Success Rate**: Feature success rate with planning vs. without
- **Rollback Frequency**: Frequency and success rate of rollbacks
- **User Adoption**: Planning skill usage across the team

## 🚨 Emergency Procedures

### Critical Issue Response

```bash
# Emergency Rollback
/plan rollback <feature> --emergency --justification "Critical production issue"

# Bypass Planning (Emergency Only)
/plan emergency --task <critical-fix> --justification "Production down"

# Retrospective Planning
/plan retrospective --task <completed-task> --analyze "post-implementation"
```

### Contact & Escalation

- **Planning Issues**: Create beads task with `planning-help` tag
- **System Failures**: Use fallback manual planning process
- **Critical Emergencies**: Direct development with retrospective documentation

## 🔧 Configuration

### Main Configuration

```yaml
# config/planning_config.yaml
planning:
  default_analysis_level: "detailed"
  auto_create_tasks: false  # User approval required
  milestone_blocking: true   # Failed milestones block progress
  
blast_radius:
  max_depth: 5
  include_tests: true
  progressive_disclosure: true
  
validation:
  ab_testing_significance: 0.95
  rollback_validation: true
  emergency_bypass: require_justification
  
flight_director:
  auto_prompt_planning: true
  complexity_threshold: "medium"
  fallback_enabled: true
```

## 📚 Examples & Use Cases

### Example 1: Feature Planning

```bash
# Agent selects task lightrag-abc from /next
Flight Director: "🎯 Task selected! Run `/plan scope lightrag-abc` to scope this task"

Agent: /plan scope lightrag-abc
# → Blast radius analysis created
# → Risk assessment completed  
# → Milestones defined

Agent: /plan proceed lightrag-abc
# → Implementation plan created
# → Beads tasks created (user approved)
# → Development starts with validation gates
```

### Example 2: Emergency Fix

```bash
Agent: /plan emergency --task fix-production-bug --justification "Production down"

System: ⚠️ EMERGENCY MODE - Minimal planning activated
→ Creates minimal blast radius analysis
→ Enables immediate development
→ Schedules retrospective planning for post-fix analysis
```

## 🆘 Troubleshooting

### Common Issues

**Planning Analysis Fails**:

- Check git repository status
- Verify beads daemon running
- Ensure proper workspace directory

**Milestone Blocking Issues**:

- Review success criteria configuration
- Check validation tool availability
- Verify test framework integration

**Orchestrator Integration**:

- Confirm Orchestrator script updates
- Check prompt configuration
- Verify session state management

### Getting Help

```bash
# Planning help
/plan help                    # General planning help
/plan help blast-radius       # Blast radius analysis help
/plan help validation         # Validation system help
/plan help emergency         # Emergency procedures help
```

---

**Status**: P0 Critical Infrastructure  
**Version**: 1.0.0  
**Last Updated**: 2026-02-05  
**Integration**: Orchestrator, Beads, TDD Gates, Git Workflow  

For issues or improvements, create a beads task with `planning-skill` tag.
