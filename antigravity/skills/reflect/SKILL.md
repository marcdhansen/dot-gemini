---
name: reflect
description: Analyzes current conversation history to extract lessons, user preferences, and corrections, then updates relevant SKILL.md files to prevent repeating mistakes. Enhanced version includes protocol integration for comprehensive learning capture.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# Reflect & Improve

## Goal

Implement "correct once, never again" philosophy by analyzing current session for "memories"—specific corrections, coding preferences, or logic improvements—and permanently documenting them into relevant `SKILL.md` files. This ensures that every mission contributes to the system's collective intelligence.

## Enhanced Features

The reflect skill now includes **protocol integration** to ensure agents understand quality requirements and can capture protocol-related learnings effectively.

## Usage

```bash
/reflect              # Original reflection
/reflect enhanced      # Enhanced reflection with protocol context
python .agent/skills/reflect/enhanced_reflection.py
```

## 🆕 Enhanced Reflection Features

### Protocol Context Integration

- **Quality Gates Overview**: Tests, linting, type checking requirements
- **Closure Standards**: File locations, quick start, documentation requirements
- **Learning Emphasis**: Real-time capture, exact error messages, user corrections
- **Common RTB Blockers**: Missing closure notes, duplicate files, uncommitted changes

### Interactive Reflection Capture

- **Session Analysis**: Recent git activity, friction log detection
- **Structured Input**: Guided questions for comprehensive learning capture
- **Protocol Issues**: Dedicated section for process and quality gate problems
- **Quantitative Results**: Metrics, performance data, success measurements

### Enhanced Data Collection

- **Technical Learnings**: Code patterns, architectural insights
- **Challenges Overcome**: Problems solved and solutions implemented
- **Process Improvements**: Workflow optimizations and friction reduction
- **Protocol Issues**: Quality gate problems and RTB blockers

## 🛠️ Tools & Scripts

### 1. `enhanced_reflection.py` (Primary Enhancement)

Comprehensive reflection system integrating protocol context with interactive learning capture.

**Features:**

- Protocol context display before reflection
- Session analysis (git activity, friction logs)
- Interactive guided reflection capture
- Structured learning categorization
- Protocol-specific issue capture
- Quantitative results tracking

**Usage**:

```bash
# Enhanced reflection with protocol integration
python .agent/skills/reflect/enhanced_reflection.py

# Captures:
# - Technical learnings
# - Challenges overcome  
# - Process improvements
# - Protocol issues
# - Quantitative results
```

### 2. Legacy Scripts (Maintained for Compatibility)

- `enhanced_reflect_system.py` - Comprehensive analysis with PFC/RTB diagnostics
- `reflect_assistant.py` - Memory discovery and rule auditing
- `skill_version_manager.py` - Version management for skill files
- `proactive_improvements.py` - Pattern analysis and suggestions

## Enhanced Workflow

### 1. Protocol Context (NEW)

Before reflection, enhanced version shows:

- Quality gate requirements
- Closure documentation standards
- Common RTB blockers
- Learning capture emphasis

### 2. Session Analysis (ENHANCED)

- Recent git activity analysis
- Friction log detection
- Current session context

### 3. Structured Reflection (ENHANCED)

**Interactive capture with prompts for:**

- Mission details and outcome
- Success metrics (key:value pairs)
- Technical learnings
- Challenges overcome
- Protocol-related issues
- Process improvements
- Quantitative results

### 4. Learning Integration (MAINTAINED)

- Automatic skill file updates
- Version tagging with learning context
- Conflict detection and resolution

### 5. Protocol Improvement (NEW)

- Identification of recurring protocol issues
- Process improvement suggestions
- Quality gate optimization insights

## 📋 Enhanced Reflection Template

Use this structure when performing enhanced reflection:

### Basic Information

- **Objective**: [Issue ID / Task Name]
- **Outcome**: [Success / Partial / Failure]
- **Duration**: [Hours spent]

### Success Metrics

- **Metric 1**: [Value]
- **Metric 2**: [Value]
- **Files Changed**: [Number]
- **Tests Passed**: [Yes/No/Partial]

### Technical Learnings

- [Learning 1]
- [Learning 2]
- [Architecture insight]
- [Performance optimization]

### Challenges Overcome

- [Challenge 1 and solution]
- [Error resolved]
- [Configuration fixed]
- [Workaround implemented]

### Protocol Issues (NEW)

- [Quality gate problem]
- [RTB blocker encountered]
- [Process friction point]
- [Documentation gap]

### Process Improvements (NEW)

- [Workflow optimization]
- [Tool improvement suggestion]
- [Time-saving approach]
- [Error prevention method]

### Quantitative Results (NEW)

## 🔍 Strategic Analysis Questions

During reflection, agents should explicitly address these strategic questions:

### Cognitive Load Reduction
>
> **QUESTION**: Are there parts of the SOP where the agent's cognitive load could be reduced by using scripts?

Consider:

- Manual steps in PFC/RTB that could be automated
- Repeated decision points that could have default behaviors
- Complex validations that could be scripted
- Information gathering that could be pre-collected

### Design Patterns & Refactoring
>
> **QUESTION**: Identify design patterns and recommended refactoring strategies.

Consider:

- Emerging patterns that should be formalized as skills
- Template-based approaches to reduce boilerplate
- Code/workflow duplication that could be consolidated
- Anti-patterns observed during the session

### Multi-Agent Collaboration
>
> **QUESTION**: What improvements could enhance parallel agent workflows?

Consider:

- Task decomposition opportunities
- Explicit dependency declarations
- Session handoff optimization
- Resource contention reduction

---

## 🎯 Benefits of Enhanced Reflection

1. **Protocol Awareness**: Agents understand quality requirements
2. **Structured Learning**: Better categorization and retrieval
3. **Process Integration**: Reflections include workflow insights
4. **Quantitative Tracking**: Measurable improvements over time
5. **Issue Prevention**: Protocol-specific learning reduces repeat problems
6. **Continuous Improvement**: Systematic process enhancement

## Integration

Enhanced reflect skill integrates with:

- **Mission Briefing**: Provides protocol context before work
- **PFC/RTB Process**: Captures protocol-related friction
- **Quality Gates**: Identifies and documents recurring issues
- **Skill Management**: Version tracking and conflict resolution
- **Process Improvement**: Systematic workflow optimization

## Advantages Over Basic Reflection

| Feature | Basic Reflection | Enhanced Reflection |
|---------|----------------|-------------------|
| Protocol Context | ❌ | ✅ |
| Interactive Capture | ❌ | ✅ |
| Session Analysis | ❌ | ✅ |
| Protocol Issues | ❌ | ✅ |
| Quantitative Results | Limited | ✅ |
| Process Improvements | Limited | ✅ |
| Structured Input | ❌ | ✅ |
| Learning Categories | Basic | Enhanced |

The enhanced reflection provides comprehensive learning capture that integrates protocol awareness with systematic improvement tracking.
