---
name: pull-request
description: >
  Creates pull requests on GitHub. Use when opening a new PR, submitting
  completed work for review on GitHub, or creating a PR after finishing
  a feature or fix.
  Do NOT use for reviewing code someone else wrote (use code-review).
  Do NOT use for committing local changes (use git).
compatibility: >
  Requires git and GitHub CLI (gh). Script at
  ~/.gemini/antigravity/skills/pull-request/scripts/create_pr.py.
metadata:
  author: Workshop Team
  version: "1.0.0"
  category: version-control
  tags: [pull-request, pr-size, quality-gates, github, code-review]
  allowed-tools: Bash, Read, Glob, Grep
---

# 🎯 Pull Request Skill

Guides agents through creating pull requests with enforced size limits and best practices.

## 📏 PR Size Limits

| Change Type | Soft Limit | Hard Limit |
|-------------|------------|------------|
| Code/Logic | 400 lines | 1000 lines |
| Docs-only | 800 lines | 2000 lines |
| Mechanical (renames, formatting) | 800 lines | 2000 lines |

**Single-file refactors over 500 lines should be split.**

## 🚨 Enforcement

- **Soft limit**: Warning - consider splitting
- **Hard limit**: BLOCKED - must split before PR
- **No exceptions** for initial release

## Usage

```bash
/pull-request
python ~/.gemini/antigravity/skills/pull-request/scripts/create_pr.py
```

---

## 📋 PR Creation Checklist

Before running `gh pr create`, verify:

### 1. Size Check ✅

```bash
# Check PR size
git diff main --stat
git diff main --shortstat
```

- [ ] Total lines changed < soft limit (or documented reason for excess)
- [ ] Single file changes < 500 lines

### 2. Branch Hygiene ✅

- [ ] Branch is up to date with main
- [ ] Commits are atomic and descriptive
- [ ] No debug code or temporary files

### 3. PR Description ✅

- [ ] Title follows convention: `[agent-xxx] Description`
- [ ] Summary of changes (2-4 sentences)
- [ ] Related issues linked
- [ ] Test coverage noted
- [ ] Breaking changes documented (if any)

### 4. Self-Review ✅

- [ ] Reviewed all changed files
- [ ] No accidental secrets/logging
- [ ] Tests pass locally

---

## 🔧 Commands

### Check PR Size

```bash
python ~/.gemini/antigravity/skills/pull-request/scripts/check_size.py
```

### Create PR (Interactive)

```bash
python ~/.gemini/antigravity/skills/pull-request/scripts/create_pr.py
```

### Non-Interactive (Automated)

```bash
# Get branch name
BRANCH=$(git branch --show-current)

# Get diff stats
git diff main --shortstat

# Create PR if size OK
gh pr create --title "feat: description" --body "$(cat <<EOF
## Summary
Brief description

## Test Plan
- [ ] Tests pass
EOF
)"
```

---

## ⚠️ Failure Modes

| Error | Solution |
|-------|----------|
| Exceeds hard limit | Split into smaller PRs |
| No changes | Commit changes first |
| Branch out of date | Rebase onto main |
| PR template missing | Add .github/pull_request_template.md |

---

## 🔗 Integration

This skill integrates with:
- **code-review**: Pre-review checks
- **finalization**: Quality gate enforcement
- **Orchestrator**: Validates PR exists before finalizing
