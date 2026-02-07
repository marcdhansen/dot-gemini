# Planning Skill Examples

This document provides practical examples of using the planning skill for common scenarios in the LightRAG project.

## Example 1: New Feature Development

### Scenario

You've selected task `lightrag-abc` from the `/next` command output and need to implement a new feature for improved query performance.

### Workflow

#### Step 1: Orchestrator Prompts Planning

```bash
🎯 TASK SELECTED - PLANNING REQUIRED
============================================================
📋 Selected Task: lightrag-abc

🚀 RECOMMENDED NEXT STEP:
   /plan scope lightrag-abc
```

#### Step 2: Scope the Task

```bash
/plan scope lightrag-abc lightrag/query.py,lightrag/core.py,docs/query_improvements.md
```

**Output:**

```text
🎯 SCOPING TASK: lightrag-abc
==================================================
📁 Analyzing 3 files...

📊 BLAST RADIUS SUMMARY:
   Risk Level: MEDIUM
   Files Affected: 3
   Testing Effort: 4-8 hours
   Deployment Impact: ROLLING
   Timeline Impact: 1-2 days

💡 RECOMMENDATIONS:
   1. Add comprehensive tests for performance improvements
   2. Update API documentation for query interface changes
   3. Consider gradual rollout with performance monitoring
```

#### Step 3: Detailed Analysis

```bash
/plan analyze lightrag-abc
```

**Output:**

```text
🔍 DETAILED ANALYSIS: lightrag-abc
==================================================

📊 SUMMARY ANALYSIS:
   Risk Level: MEDIUM
   Critical Paths: lightrag/core.py
   Estimated Testing: 4-8 hours

🔍 DETAILED IMPACTS:
   📁 lightrag/query.py
      Risk: MEDIUM
      Complexity: 6.2
      Test Coverage: 75.0%
   📁 lightrag/core.py
      Risk: HIGH
      Complexity: 8.5
      Test Coverage: 85.0%

📋 RECOMMENDED TASKS (3):
   1. Add comprehensive test coverage for lightrag-abc [P2]
   2. Update documentation for lightrag-abc [P3]
   3. Performance testing for lightrag-abc [P2]
```

#### Step 4: Create Implementation Plan

```bash
/plan proceed lightrag-abc
```

**Interactive Selection:**

```text
📋 RECOMMENDED TASKS (3):

1. Add comprehensive test coverage for lightrag-abc [P2]
   📝 Create comprehensive tests for changes in lightrag-abc...
   ⏱️  Estimate: 4-8 hours
   🏷️  Tags: testing, quality-assurance

2. Update documentation for lightrag-abc [P3]
   📝 Update documentation to reflect changes in lightrag-abc...
   ⏱️  Estimate: 2-4 hours
   🏷️  Tags: documentation

3. Performance testing for lightrag-abc [P2]
   📝 Create and execute performance tests for lightrag-abc...
   ⏱️  Estimate: 4-6 hours
   🏷️  Tags: performance, testing

💡 Enter the numbers of tasks you want to create (comma-separated)
   Example: 1,3
Your selection: 1,3
```

**Final Output:**

```text
🚀 PROCEEDING WITH IMPLEMENTATION: lightrag-abc
============================================================
✅ Created 2 additional tasks in Beads
   - lightrag-def - Add comprehensive test coverage for lightrag-abc
   - lightrag-ghi - Performance testing for lightrag-abc

🎯 IMPLEMENTATION PLAN CREATED
   Task: lightrag-abc
   Milestones: 2
   Approved Tasks: 2

🎯 MILESTONES:
   1. Development [NOT_STARTED] 🚫
      Duration: 2-3 days
      Criteria: 2
   2. Integration [NOT_STARTED] 🚫
      Duration: 1-2 days
      Criteria: 1

🎉 Implementation plan ready!
💡 Track progress with: /plan track lightrag-abc
```

## Example 2: Emergency Bug Fix Scenario

### Scenario

Production is down and you need to fix a critical issue immediately.

#### Emergency Planning

```bash
/plan scope lightrag-critical-fix lightrag/api/routes.py --level summary
```

**Output:**

```
🎯 SCOPING TASK: lightrag-critical-fix
==================================================
📁 Analyzing 1 files...

📊 BLAST RADIUS SUMMARY:
   Risk Level: CRITICAL
   Files Affected: 1
   Testing Effort: 2-4 hours
   Deployment Impact: ROLLING
   Timeline Impact: 2-3 weeks

🚨 CRITICAL CHANGES DETECTED:
💡 Recommendations:
   1. Consider breaking this into smaller, manageable changes
   2. Create detailed rollback plan before starting
   3. Schedule comprehensive testing including edge cases
```

#### Proceed with Emergency Fix

```bash
/plan proceed lightrag-critical-fix
```

**Emergency Mode Output:**

```
🚀 PROCEEDING WITH IMPLEMENTATION: lightrag-critical-fix
============================================================
⚠️ EMERGENCY MODE - Minimal planning activated
✅ Created minimal plan with basic risk assessment
⏰ Schedule retrospective planning for post-fix analysis

🎯 EMERGENCY IMPLEMENTATION PLAN:
   Immediate Actions:
   - Create feature branch
   - Implement core fix
   - Basic testing
   - Deploy with monitoring
   
   Rollback Steps:
   - Revert to previous commit
   - Verify functionality restored
   - Monitor system stability

🎉 Emergency implementation plan ready!
💡 Monitor closely and schedule retrospective planning
```

## Example 3: Database Migration Scenario

### Scenario

You need to implement a database schema migration for the knowledge graph storage.

#### Comprehensive Planning

```bash
/plan scope lightrag-db-migration lightrag/storage/database.py,migrations/001_graph_schema.sql
```

**Output:**

```
🎯 SCOPING TASK: lightrag-db-migration
==================================================
📁 Analyzing 2 files...

📊 BLAST RADIUS SUMMARY:
   Risk Level: CRITICAL
   Files Affected: 2
   Testing Effort: 2-4 days
   Deployment Impact: FULL_RESTART
   Timeline Impact: 2-3 weeks

💡 RECOMMENDATIONS:
   1. Create detailed rollback plan before starting
   2. Schedule comprehensive testing including edge cases
   3. Consider canary deployment approach

🗄️  MIGRATION REQUIREMENTS:
   - Database migration scripts needed
   - Configuration migration needed
```

#### Detailed Analysis

```bash
/plan analyze lightrag-db-migration
```

**Output:**

```
📋 RECOMMENDED TASKS (4):
   1. Database migration for lightrag-db-migration [P1]
   2. Add comprehensive test coverage for lightrag-db-migration [P1]
   3. Risk mitigation and rollback planning for lightrag-db-migration [P0]
   4. Performance testing for lightrag-db-migration [P2]
```

#### Create Implementation Plan

```bash
/plan proceed lightrag-db-migration
```

**Select All Tasks:**

```
💡 Enter the numbers of tasks you want to create (comma-separated)
Your selection: 1,2,3,4
```

**Output:**

```
🎯 IMPLEMENTATION PLAN CREATED
   Task: lightrag-db-migration
   Milestones: 3
   Approved Tasks: 4

🎯 MILESTONES:
   1. Development [NOT_STARTED] 🚫
      Duration: 5-7 days
      Criteria: 2
   2. Integration [NOT_STARTED] 🚫
      Duration: 1-2 days
      Criteria: 1
   3. Additional Requirements [NOT_STARTED] 🚫
      Duration: 3 days
      Criteria: 3
```

## Example 4: Task Tabling Scenario

### Scenario

You scoped a task but don't have resources to complete it now.

#### Table the Task

```bash
/plan table lightrag-abc "Waiting for Q2 resources"
```

**Output:**

```
📋 TABLED TASK: lightrag-abc
========================================
💡 Reason: Waiting for Q2 resources

✅ Task tabled with scoping saved
   Risk Level: MEDIUM
   Files: 3

💡 Use /next to select a different task
```

## Example 5: Tracking Scenario

### Scenario

You want to check the progress of an ongoing task.

#### Track Progress

```bash
/plan track lightrag-abc
```

**Output:**

```
📊 TRACKING PROGRESS: lightrag-abc
========================================

📊 OVERALL STATUS:
   Task: lightrag-abc
   Implementation: 75.0%
   Validation: 50.0%
   Overall: 62.5%
   🔄 IN PROGRESS

✅ COMPLETED MILESTONES:
   - Development: All core functions implemented, Unit tests passing with >80% coverage

🚫 BLOCKED VALIDATION:
   - Integration: Integration tests failing - See validation/lightrag-abc_blocked.json
```

## Example 6: Rollback Scenario

### Scenario

A deployment is causing issues and needs to be rolled back.

#### Execute Rollback

```bash
/plan rollback query-performance-improvement "Severe performance regression in production"
```

**Output:**

```
🔄 ROLLBACK: query-performance-improvement
========================================
   Justification: Severe performance regression in production
   Rollback steps: 4

   Step 1/4: git checkout previous-stable
   ✅ Step completed
   
   Step 2/4: docker-compose down
   ✅ Step completed
   
   Step 3/4: docker-compose up -d
   ✅ Step completed
   
   Step 4/4: run-health-checks
   ⚠️  Data consistency check failed: query_response_time

🔄 Executing rollback for query-performance-improvement
   Justification: Severe performance regression in production
   Rollback steps: 4
   Step 1/4: git checkout previous-stable - ✅
   Step 2/4: docker-compose down - ✅
   Step 3/4: docker-compose up -d - ✅
   Step 4/4: run-health-checks - ✅

⚠️  Data consistency check failed: query_response_time

✅ Rollback completed for query-performance-improvement
```

## Example 7: Blast Radius Scenario

### Scenario

You want to quickly understand the impact of some changes.

#### Quick Analysis

```bash
/plan blast-radius lightrag/api/routes.py lightrag/core.py --level summary
```

**Output:**

```
💥 BLAST RADIUS ANALYSIS
========================================
Files: 2
Level: summary

📊 SUMMARY:
   Risk Level: HIGH
   Files Affected: 2
   Critical Paths: lightrag/core.py
   Testing Effort: 1-2 days
   Deployment Impact: ROLLING
   Timeline Impact: 1-2 weeks

💡 RECOMMENDATIONS:
   1. Plan thorough testing and review process
   2. Monitor key metrics during deployment
   3. Consider canary deployment approach
```

## Example 8: Conflict Scenario

### Scenario

There's an existing manual plan that conflicts with the planning skill.

#### Fallback to Manual Planning

The system detects the conflict and automatically provides fallback options:

```
🔄 CONFLICT DETECTED: Existing manual plan found for lightrag-legacy-feature

🔧 FALLBACK ACTIVATED: Merge with existing plan

✅ Successfully merged planning analysis with existing manual plan
   Original plan: docs/legacy_feature_plan.md
   Files analyzed: 4
   Enhanced with blast radius analysis

💡 You can now proceed with enhanced manual plan or use combined approach
```

## Example 9: Validation Scenario

### Scenario

You need to check if validation gates are passed for a task.

#### Check Validation

```bash
/plan validate lightrag-abc
```

**Output:**

```
✅ VALIDATING PLAN: lightrag-abc
========================================

🎯 VALIDATION STATUS: in_progress
   Progress: 50.0%
   Milestones: 2/4

🎯 MILESTONES:
   • Development: completed
   • Integration: failed
   • Performance Testing: not_started
   • Security Review: not_started

   🚫 BLOCKED - See validation/lightrag-abc_blocked.json
```

## Example 10: Resource Scenario

### Scenario

System resources are constrained, preventing full planning.

#### Automatic Fallback

```
⚠️  RESOURCE CONSTRAINTS DETECTED

⏸️  TASK DEFERRED: lightrag-resource-heavy-feature
   Reason: System resources unavailable
   
💡 Task has been queued for retry when resources are available
   Automatic retry scheduled in 24 hours
   Planning requirements saved for later completion

💡 For immediate work, select a different task with /next
```

---

## Best Practices

### 1. Always Start with Scoping

```bash
/plan scope <task-id> [files...]
```

Scoping provides the foundation for all subsequent planning decisions.

### 2. Review Recommendations Before Proceeding

```bash
/plan analyze <task-id>
```

Use the detailed analysis to understand the full impact before committing.

### 3. Track Progress Regularly

```bash
/plan track <task-id>
```

Regular tracking helps identify issues early and keeps stakeholders informed.

### 4. Use Rollback Safety Nets

Always ensure rollback procedures are validated before deployment:

```bash
/plan validate-rollback <feature-name>
```

### 5. Handle Conflicts Gracefully

The planning skill automatically detects and handles conflicts, but understanding the fallback mechanisms helps you make better decisions.

### 6. Emergency Planning

For critical issues, use summary-level analysis to get quick insights:

```bash
/plan scope <task-id> --level summary
```

### 7. Documentation Integration

The planning skill automatically creates and updates relevant documentation. Always review the generated documents for accuracy.

---

## Troubleshooting

### Common Issues and Solutions

**Issue:** `/plan scope` fails with "No changed files detected"
**Solution:** Provide file list manually or check git status

**Issue:** Task creation in beads fails
**Solution:** Check beads daemon status and network connectivity

**Issue:** Validation blocks progress
**Solution:** Check validation logs and address failed criteria

**Issue:** Rollback procedures fail
**Solution:** Ensure rollback plans are validated and tested in staging

**Issue:** Planning skill unavailable
**Solution:** Use fallback mechanisms or manual planning guidance

For additional help, use:

```bash
/plan help
```

---

*This examples document covers the most common use cases for the planning skill. For specific questions or edge cases, consult the main skill documentation or use the built-in help system.*
