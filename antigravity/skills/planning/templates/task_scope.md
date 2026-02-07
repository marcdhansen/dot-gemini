# Task Scoping Template

## Task Overview

**Task ID:** {{task_id}}
**Task Title:** {{task_title}}
**Scoping Date:** {{scoping_date}}
**Analysis Level:** {{analysis_level}}
**Planned By:** {{planner_name}}

## Task Description

{{task_description}}

## Blast Radius Analysis

### Summary Assessment

- **Risk Level:** {{risk_level}}
- **Files Affected:** {{files_affected_count}}
- **Estimated Testing Effort:** {{testing_effort}}
- **Deployment Impact:** {{deployment_impact}}

### Critical Paths

{{#each critical_paths}}

- {{this}}
{{/each}}

## Detailed Impact Analysis

### File-by-File Impact

{{#each file_impacts}}

#### {{path}}

- **Change Type:** {{change_type}}
- **Risk Level:** {{risk_level}}
- **Complexity Score:** {{complexity_score}}
- **Test Coverage:** {{test_coverage}}%
- **Dependencies Affected:** {{dependencies_affected_count}}

**Dependencies:**
{{#each dependencies_affected}}

- {{this}}
{{/each}}

{{/each}}

### Cross-Module Dependencies

{{#each cross_module_dependencies}}

- {{this}}
{{/each}}

## Recommendations

### Primary Recommendations

{{#each primary_recommendations}}

- {{this}}
{{/each}}

### Risk Mitigation

{{#each risk_mitigation}}

- **{{area}}:** {{strategy}}
{{/each}}

### Testing Requirements

{{#each testing_requirements}}

- **{{type}}:** {{description}}
{{/each}}

## Additional Tasks Recommended

Based on the blast radius analysis, the following additional tasks are recommended:

{{#each recommended_tasks}}

### {{title}} [{{priority}}]

**Description:** {{description}}
**Estimate:** {{estimate}}
**Dependencies:** {{dependencies}}
**Reason:** {{recommendation_reason}}

{{/each}}

## Implementation Approach

### Suggested Approach

{{suggested_approach}}

### Estimated Timeline

- **Core Development:** {{core_development_time}}
- **Testing:** {{testing_time}}
- **Integration:** {{integration_time}}
- **Total:** {{total_time}}

### Resource Requirements

- **Development:** {{dev_resources}}
- **Testing:** {{test_resources}}
- **Review:** {{review_resources}}

## Decision Options

Based on this scoping analysis, you have the following options:

### Option 1: Proceed with Implementation

**When to choose:** Risk level is acceptable and resources are available
**Next steps:**

- Run `/plan proceed {{task_id}}` to create implementation plan
- Review and approve recommended additional tasks
- Begin development following the implementation plan

### Option 2: Modify the Approach

**When to choose:** Risk level is high but task is important
**Next steps:**

- Consider breaking into smaller sub-tasks
- Increase resource allocation
- Add additional risk mitigation measures
- Run `/plan scope {{task_id}}` again with modified approach

### Option 3: Table for Later

**When to choose:** Risk level is too high or resources unavailable
**Next steps:**

- Run `/plan table {{task_id}} <reason>` to save scoping
- Schedule for when resources are available
- Consider alternative approaches to reduce risk

## Quality Gates

### Pre-Development Checks

- [ ] Risk level is acceptable ({{risk_level}})
- [ ] Required resources are available
- [ ] Dependencies are clear and manageable
- [ ] Rollback plan is feasible

### During Development Checks

- [ ] Code review completed for all changes
- [ ] Test coverage meets requirements ({{test_coverage_threshold}}%)
- [ ] Integration tests pass
- [ ] Performance impact is acceptable

## Risk Assessment Summary

| Risk Factor | Level | Mitigation |
|-------------|-------|------------|
| Technical Complexity | {{technical_complexity}} | {{technical_mitigation}} |
| Dependencies | {{dependency_risk}} | {{dependency_mitigation}} |
| Testing Coverage | {{testing_risk}} | {{testing_mitigation}} |
| Rollback Complexity | {{rollback_risk}} | {{rollback_mitigation}} |

## Next Steps

1. **Review this scoping document** carefully
2. **Choose your approach:** Proceed, Modify, or Table
3. **Execute the appropriate command:**
   - `/plan proceed {{task_id}}` to create implementation plan
   - `/plan analyze {{task_id}}` for more detailed analysis
   - `/plan table {{task_id}} <reason>` to save and defer

## Contact Information

**Planning Questions:** Use `/plan help` for assistance
**Technical Questions:** Contact the development team
**Process Questions:** Contact the Orchestrator

---
*This scoping document was generated using the LightRAG Planning Skill*
*Last Updated: {{last_updated}}*
*For the most current analysis, run `/plan analyze {{task_id}}`*
