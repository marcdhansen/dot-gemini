# Feature Planning Template

## Feature Overview

**Feature Name:** {{feature_name}}
**Task ID:** {{task_id}}
**Beads Issue:** {{beads_issue_id}} ({{beads_issue_status}})
**Created:** {{creation_date}}
**Priority:** {{priority}}
**Estimated Duration:** {{estimated_duration}}

## Description

{{feature_description}}

## Objectives

{{#each objectives}}

- {{this}}
{{/each}}

## API Design

{{#if is_api_change}}

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
{{#each api_endpoints}}
| {{method}} | {{path}} | {{description}} |
{{/each}}

### Request Format

```json
{{request_example}}
```

### Response Format

```json
{{response_example}}
```

### Breaking Changes

{{#each breaking_changes}}

- {{this}}
{{/each}}
{{#unless breaking_changes}}
- None
{{/unless}}

### Backward Compatibility

- [ ] Full backward compatible
- [ ] Requires version bump
- [ ] Deprecated endpoints remain available until:

{{else}}

*No API changes for this feature.*

{{/if}}

## Blast Radius Analysis

### Risk Assessment

- **Risk Level:** {{risk_level}}
- **Files Affected:** {{files_affected_count}}
- **Critical Paths:** {{critical_paths}}

### Impact Summary

- **Testing Effort:** {{testing_effort}}
- **Deployment Impact:** {{deployment_impact}}
- **Timeline Impact:** {{timeline_impact}}

### Affected Components

{{#each affected_components}}

#### {{name}}

- **Type:** {{type}}
- **Risk Level:** {{risk_level}}
- **Dependencies:** {{dependencies}}
- **Test Coverage:** {{test_coverage}}%
{{/each}}

## Implementation Plan

### Milestones

{{#each milestones}}

#### {{name}}

- **Description:** {{description}}
- **Estimated Duration:** {{estimated_duration}}
- **Blocking:** {{blocking}}
- **Success Criteria:**
{{#each success_criteria}}
  - {{metric_name}} {{comparison_operator}} {{threshold_value}}
{{/each}}
{{/each}}

### Dependencies

{{#each dependencies}}

- **{{name}}:** {{description}} ({{priority}})
{{/each}}

## Risk Mitigation

### High-Risk Areas

{{#each risk_areas}}

- **{{area}}:** {{mitigation_strategy}}
{{/each}}

### Rollback Plan

- **Rollback Complexity:** {{rollback_complexity}}
- **Estimated Rollback Time:** {{rollback_time}}
- **Data Consistency Checks:**
{{#each consistency_checks}}
  - {{this}}
{{/each}}

## Testing Strategy

### Test Coverage Requirements

- **Unit Tests:** {{unit_test_coverage}}% coverage required
- **Integration Tests:** {{integration_test_requirements}}
- **Performance Tests:** {{performance_test_requirements}}

### Test Environment Requirements

{{#each test_environments}}

- **{{name}}:** {{requirements}}
{{/each}}

## Resource Requirements

### Human Resources

- **Development:** {{dev_resources}}
- **Testing:** {{test_resources}}
- **Review:** {{review_resources}}

### Technical Resources

- **Infrastructure:** {{infrastructure_requirements}}
- **Tools:** {{tool_requirements}}
- **Access:** {{access_requirements}}

## Timeline

### Phases

{{#each phases}}

#### {{name}} ({{duration}})

{{#each tasks}}

- {{name}}: {{duration}}
{{/each}}
{{/each}}

### Key Dates

- **Start Date:** {{start_date}}
- **Milestone 1:** {{milestone_1_date}}
- **Milestone 2:** {{milestone_2_date}}
- **Completion:** {{completion_date}}

## Communication Plan

### Stakeholders

{{#each stakeholders}}

- **{{name}}:** {{role}} - {{communication_frequency}}
{{/each}}

### Reporting

- **Status Updates:** {{status_update_frequency}}
- **Progress Reports:** {{progress_report_frequency}}
- **Escalation:** {{escalation_process}}

## Post-Implementation

### Monitoring Requirements

{{#each monitoring_requirements}}

- {{metric}}: {{threshold}}
{{/each}}

### Success Metrics

{{#each success_metrics}}

- {{name}}: {{target}} ({{measurement_method}})
{{/each}}

### Documentation Updates

{{#each documentation_updates}}

- {{type}}: {{description}}
{{/each}}

## Beads Issue Tracking

{{#each beads_issues}}

### {{issue_id}}
- **Type:** {{type}}
- **Status:** {{status}}
- **Priority:** {{priority}}
- **Created:** {{created_date}}
{{/each}}

## Approval

**Planned By:** {{planner_name}}
**Reviewed By:** {{reviewer_name}}
**Approved By:** {{approver_name}}

**Approval Date:** {{approval_date}}
**Last Updated:** {{last_updated}}

---
*This planning document was generated using the LightRAG Planning Skill*
*For questions or updates, use the planning skill commands*
