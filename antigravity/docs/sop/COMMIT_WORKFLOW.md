# Commit & Merge Workflow

Simple rules for clean git history.

## When to Commit

| Situation | Action |
|-----------|--------|
| Working on a task | Commit often with clear messages |
| Task complete | Ensure clean commit before PR |
| Multiple changes | Squash before merge to main |

## Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Examples:
```
feat(agent): Add optional SOP support

fix(parser): Handle missing field gracefully

docs(readme): Update installation instructions
```

## Merge Rules

1. **Never merge directly to main** - Always use PR
2. **Squash commits** - One commit per logical change
3. **Rebase on main** - Before PR, rebase: `git rebase origin/main`
4. **Force push only to your branch** - Never force push main

## Common Commands

```bash
# Check current status
git status

# Stage changes
git add <files>

# Commit with message
git commit -m "feat(scope): description"

# Rebase on main before PR
git fetch origin
git rebase origin/main

# Interactive squash (if needed)
git rebase -i origin/main

# Force push your branch (safe for feature branches)
git push --force-with-lease

# Create PR
gh pr create --fill
```

## Troubleshooting

### "Merge conflict detected"
```bash
# Resolve conflicts, then
git add <resolved-files>
git rebase --continue
```

### "Commit already pushed"
- Never amend commits that are pushed
- Create a new commit to fix instead

### "Main has advanced"
```bash
git fetch origin
git rebase origin/main
# Fix any conflicts
git push --force-with-lease
```
