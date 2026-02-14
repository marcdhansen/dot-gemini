---
name: code-review
description: Checklist-based code review skill for identifying logic errors, ensuring test coverage, and validating PR size.
allowed-tools: Bash, Read, Glob, Grep
---

# 🛡️ Code Review Skill

The `code-review` skill provides automated and interactive code review capabilities for agents. It ensures that all changes meet quality standards before they are finalized.

## 🚨 MANDATORY: Finalization Gate

> [!CAUTION]
> If this skill is invoked during finalization and "Request Changes" is selected, **it MUST block Git operations (commits/pushes)** until the issues are resolved.

## Usage

```bash
/code-review
python ~/.gemini/antigravity/skills/code-review/scripts/code_review.py
```

---

## 🤖 Automated Pre-Review Checks

### Before Requesting Review

Agent should run automated checks before creating PR or requesting review:

```bash
#!/bin/bash
# scripts/pre_review_checks.sh

echo "🔍 Running Pre-Review Automated Checks..."
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0
BLOCKERS=""

# 1. Linting Check
echo "1. Linting (ruff)..."
if ruff check .; then
    echo "   ✅ No linting issues"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "   ❌ Linting issues found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
    BLOCKERS="$BLOCKERS\n- Linting issues must be fixed"
fi

# 2. Type Checking
echo ""
echo "2. Type Checking (mypy)..."
if mypy .; then
    echo "   ✅ Type checking passed"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "   ⚠️ Type checking issues (non-blocking)"
fi

# 3. Security Scan
echo ""
echo "3. Security Scan (bandit)..."
bandit -r src/ -f json -o .security_report.json
SECURITY_ISSUES=$(jq '[.results[] | select(.issue_severity == "HIGH" or .issue_severity == "MEDIUM")] | length' .security_report.json)

if [ "$SECURITY_ISSUES" -eq 0 ]; then
    echo "   ✅ No security issues"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "   ⚠️ $SECURITY_ISSUES security issues found (review required)"
    echo "   See: .security_report.json"
fi

# 4. Test Coverage
echo ""
echo "4. Test Coverage..."
coverage run -m pytest
coverage report --fail-under=80

if [ $? -eq 0 ]; then
    echo "   ✅ Coverage ≥80%"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    COVERAGE=$(coverage report | tail -1 | grep -oE '[0-9]+%' | grep -oE '[0-9]+')
    echo "   ⚠️ Coverage: ${COVERAGE}% (target: 80%)"
    
    # Check if coverage decreased
    BASELINE_COVERAGE=$(git show origin/main:.coverage_baseline || echo "80")
    if [ "$COVERAGE" -lt "$BASELINE_COVERAGE" ]; then
        echo "   ❌ Coverage decreased (was: ${BASELINE_COVERAGE}%)"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        BLOCKERS="$BLOCKERS\n- Coverage must not decrease"
    fi
fi

# 5. New Functions Have Tests
echo ""
echo "5. Test Coverage for New Code..."
NEW_FUNCTIONS=$(git diff origin/main --cached | grep -E '^\+\s*def ' | grep -v '__init__' | wc -l)
NEW_TESTS=$(git diff origin/main --cached tests/ | grep -E '^\+\s*def test_' | wc -l)

echo "   New functions: $NEW_FUNCTIONS"
echo "   New tests: $NEW_TESTS"

if [ "$NEW_FUNCTIONS" -gt 0 ]; then
    if [ "$NEW_TESTS" -ge "$NEW_FUNCTIONS" ]; then
        echo "   ✅ All new functions have tests"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo "   ❌ Missing tests for new functions"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        BLOCKERS="$BLOCKERS\n- All new functions must have tests"
    fi
else
    echo "   ✅ No new functions (N/A)"
fi

# 6. Breaking Changes Detection
echo ""
echo "6. Breaking Changes Check..."
BREAKING_CHANGES=$(git diff origin/main --cached | grep -E '^\-\s*def.*\(.*\):' | wc -l)

if [ "$BREAKING_CHANGES" -gt 0 ]; then
    echo "   ⚠️ $BREAKING_CHANGES potential breaking changes detected"
    echo "   Review API signature changes carefully"
else
    echo "   ✅ No breaking API changes"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# 7. Large PR Check
echo ""
echo "7. PR Size Check..."
LINES_CHANGED=$(git diff origin/main --cached --shortstat | grep -oE '[0-9]+ insertion|[0-9]+ deletion' | grep -oE '[0-9]+' | awk '{sum+=$1} END {print sum}')

if [ -z "$LINES_CHANGED" ]; then
    LINES_CHANGED=0
fi

if [ "$LINES_CHANGED" -lt 500 ]; then
    echo "   ✅ PR size: $LINES_CHANGED lines (good)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
elif [ "$LINES_CHANGED" -lt 1000 ]; then
    echo "   ⚠️ PR size: $LINES_CHANGED lines (large - consider splitting)"
else
    echo "   ❌ PR size: $LINES_CHANGED lines (too large - must split)"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
    BLOCKERS="$BLOCKERS\n- PR must be split (>1000 lines)"
fi

# Summary
echo ""
echo "================================"
echo "Pre-Review Check Summary"
echo "================================"
echo "Passed: $CHECKS_PASSED"
echo "Failed: $CHECKS_FAILED"

if [ "$CHECKS_FAILED" -gt 0 ]; then
    echo ""
    echo "❌ BLOCKERS FOUND:"
    echo -e "$BLOCKERS"
    echo ""
    echo "Please fix blockers before requesting review."
    exit 1
else
    echo ""
    echo "✅ All pre-review checks passed!"
    echo "Ready for human review."
    exit 0
fi
```

### Integration with PR Creation

```bash
# Before creating PR, run pre-review checks
/code-review --pre-review

# If checks pass, proceed
if [ $? -eq 0 ]; then
    gh pr create --title "feat: add user authentication" --body "..."
else
    echo "Fix issues before creating PR"
    exit 1
fi
```

### Self-Review Checklist for Implementing Agent

Before requesting review, agent should complete:

```markdown
## Self-Review Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] No commented-out code or debug prints
- [ ] Variable/function names are clear and descriptive
- [ ] Complex logic has explanatory comments
- [ ] No code duplication (DRY principle)

### Testing
- [ ] All new functions have tests
- [ ] Edge cases covered
- [ ] Tests pass locally
- [ ] Coverage not decreased
- [ ] Manual testing performed (if applicable)

### Documentation
- [ ] Docstrings added for new functions/classes
- [ ] README updated if needed
- [ ] API changes documented
- [ ] Migration guide included (for breaking changes)

### Git Hygiene
- [ ] Commits are atomic (one logical change per commit)
- [ ] Commit messages are clear and descriptive
- [ ] No merge commits (rebased on main)
- [ ] No unrelated changes included

### Performance & Security
- [ ] No obvious performance issues
- [ ] No security vulnerabilities introduced
- [ ] Secrets not committed
- [ ] Input validation present where needed

### Review Readiness
- [ ] PR size reasonable (<500 lines ideal)
- [ ] PR description explains changes
- [ ] Screenshots/examples provided (if UI changes)
- [ ] Known limitations documented
```

### Automated Review Report Generation

```bash
#!/bin/bash
# scripts/generate_review_report.sh

# Generate comprehensive report for reviewers

cat > .review_report.md << EOF
# Code Review Report

## Summary
- **Files Changed**: $(git diff origin/main --cached --name-only | wc -l)
- **Lines Added**: $(git diff origin/main --cached --shortstat | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
- **Lines Removed**: $(git diff origin/main --cached --shortstat | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+')
- **Test Coverage**: $(coverage report | tail -1 | grep -oE '[0-9]+%')

## Automated Checks

### Linting
\`\`\`
$(ruff check . 2>&1 || echo "No issues")
\`\`\`

### Security Scan
\`\`\`
$(bandit -r src/ -f txt 2>&1 | tail -20)
\`\`\`

### Type Checking
\`\`\`
$(mypy . 2>&1 | head -20)
\`\`\`

## Changes by Category

### New Functions
\`\`\`
$(git diff origin/main --cached | grep -E '^\+\s*def ')
\`\`\`

### Modified Functions
\`\`\`
$(git diff origin/main --cached | grep -E '^\-\s*def ')
\`\`\`

### New Tests
\`\`\`
$(git diff origin/main --cached tests/ | grep -E '^\+\s*def test_')
\`\`\`

## Complexity Analysis
$(radon cc src/ -a -nc)

## Self-Review Notes
[Agent should fill this in]

- Main changes: ...
- Potential concerns: ...
- Alternatives considered: ...
- Testing approach: ...

EOF

echo "Review report generated: .review_report.md"
```

## Enhanced Review Flow

### For Implementing Agent

```bash
# 1. Complete work
git add .
git commit -m "feat: add user authentication"

# 2. Run self-review
/code-review --self-review

# Output:
# Running Self-Review...
# 
# Code Quality:
# ✅ Linting: No issues
# ✅ Type checking: Passed
# ⚠️ Complexity: 2 functions with high complexity
#    - authenticate_user: CC=12 (threshold: 10)
#    - validate_token: CC=11 (threshold: 10)
# 
# Testing:
# ✅ All new functions tested
# ✅ Coverage: 87% (baseline: 85%)
# ✅ All tests pass
# 
# Self-Review Checklist:
# ❌ INCOMPLETE - Missing:
#    - Docstrings for authenticate_user()
#    - README update for new API endpoints
# 
# Please complete checklist before requesting review.

# 3. Fix issues
# ... add docstrings, update README ...

# 4. Re-run self-review
/code-review --self-review
# ✅ Self-review complete!

# 5. Generate review report
/code-review --generate-report

# 6. Create PR
gh pr create --title "feat: add user authentication" \
  --body "$(cat .review_report.md)"

# 7. Request review
gh pr review --request @reviewer
```

### Configuration

Add to code-review/config/defaults.yaml:

```yaml
automated_checks:
  linting:
    tool: ruff
    blocking: true
  
  type_checking:
    tool: mypy
    blocking: false  # Warn but don't block
  
  security:
    tool: bandit
    severity_threshold: MEDIUM
    blocking_on: HIGH
  
  coverage:
    minimum: 80
    allow_decrease: false
  
  complexity:
    max_complexity: 10
    tool: radon
  
  pr_size:
    warning: 500
    blocking: 1000

self_review_checklist:
  required_sections:
    - code_quality
    - testing
    - documentation
    - git_hygiene
  
  blocking_incomplete: true
```

---

## Purpose

This skill performs a multi-stage code review:

1. **Logic Correctness**: Analyzes diffs for potential logic errors or regressions.
2. **Test Coverage**: Verifies that new functionality includes corresponding tests.
3. **PR Size Validation**: Checks if the total changes exceed recommended thresholds (default: 500 lines).
4. **Interactive Checklist**: Prompts the agent to verify critical items.

## Implementation

- **Core Logic**: `~/.gemini/antigravity/skills/code-review/scripts/code_review.py`
- **Configuration**: `~/.gemini/antigravity/skills/code-review/config/defaults.yaml`
- **Gate Enforcement**: Integrated with Orchestrator finalization phase.

## Configuration

Default settings in `config/defaults.yaml`:

```yaml
max_diff_lines: 500
require_tests: true
block_on_request_changes: true
```

## Error Handling

- **Large Diffs**: Warns if the diff is too large for effective review.
- **Missing Tests**: Flags missing tests for new code files.
- **User Intervention**: Allows manual override if necessary (logged).

## Integration

- **Orchestrator**: Blocks finalization if the review status is `REQUEST_CHANGES`.
- **Beads**: Links review outcomes to the active task.

## P0 Review Issue Protocol

When assigned a P0 PR review issue:

1. **Read Issue**: Open the PR link from the issue description
2. **Run Review**: `python ~/.gemini/antigravity/skills/code-review/scripts/code_review.py`
3. **Complete Checklist**: Answer all interactive checklist items
4. **Document Outcome**: Update the issue with your review outcome

### Outcomes

| Decision | Action |
| --- | --- |
| **APPROVE** | Close the issue → Unblocks PR merge |
| **REQUEST_CHANGES** | Add comment with required changes → Keep issue open |

### Reviewer: Requesting Decomposition

When a PR covers multiple independent concerns, request decomposition using this structured format:

```markdown
## 🔄 REQUEST_CHANGES: Decomposition Required

This PR covers multiple independent concerns. Please decompose into focused child PRs per the [PR Response Protocol](~/.agent/docs/sop/pr-response-protocol.md).

**Identified Concerns**:
1. <Concern 1 description>
2. <Concern 2 description>  
3. <Concern 3 description>

**Recommended Decomposition**:
- Child PR 1: <scope>
- Child PR 2: <scope>
- Child PR 3: <scope>

**Next Steps**:
- [ ] Close this PR
- [ ] Create Epic/Parent issue  
- [ ] Create child issues for each concern
- [ ] Create focused child PRs (<200 lines each)
```

**Thrashing Detection**: If a PR has already been rejected once, strongly consider requesting decomposition to prevent thrashing. After ≥2 rejections, decomposition is **MANDATORY** per the protocol.

### Implementing Agent: After REQUEST_CHANGES

If your PR receives `REQUEST_CHANGES`, you MUST follow the [PR Response Protocol](~/.agent/docs/sop/pr-response-protocol.md).

**Quick Reference**:

- **Minor fixes** → Fix inline, push fixup commits, re-request review
- **Major rework (single concern)** → Assess scope, rework if focused, else decompose
- **Decomposition requested or ≥2 rejections** → **MANDATORY decomposition** (close PR, create Epic/child issues/PRs)

**Full Protocol**: [PR Response Protocol](~/.agent/docs/sop/pr-response-protocol.md)

### 🚀 Merging Protocol

After approving a PR, always use the **"Squash and merge"** option on GitHub to maintain a clean atomic history.

- **Automation**: Use the `browser_subagent` to navigate to the PR URL and explicitly select "Squash and merge" from the dropdown before confirming.
- **Verification**: Ensure the final merged commit follows the conventional format and includes the issue ID.

> [!IMPORTANT]
> The reviewing agent MUST be different from the implementing agent. This is enforced by Beads task assignment.
