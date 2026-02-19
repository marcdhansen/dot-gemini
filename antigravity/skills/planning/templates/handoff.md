# Handoff: {{issue_id}}

## Overview

**Issue ID:** {{issue_id}}
**Feature:** {{feature_name}}
**Created:** {{creation_date}}
**Current Status:** {{status}}

## Current Status

- [ ] Task 1: {{task_1}}
- [ ] Task 2: {{task_2}}
- [ ] Task 3: {{task_3}}

## Completed

{{#each completed_items}}

- {{this}}
{{/each}}

## Remaining

{{#each remaining_items}}

- {{this}}
{{/each}}

## Blockers

{{#each blockers}}

- {{this}}
{{/each}}
{{#unless blockers}}
- None
{{/unless}}

## Context

{{handoff_context}}

## Plan Link

See: [Implementation Plan](../plans/{{issue_id}}.md)

## PR Link

{{pr_url}}

---

*This handoff was generated during session finalization.*
*File will be automatically deleted when the associated beads issue is closed after PR merge.*
