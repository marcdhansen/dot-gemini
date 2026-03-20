# 🧶 Standard Git Workflow

> **Purpose**: Ensure clean, linear, and audit-ready project history.
> **Scope**: All feature development and hotfixes.

---

## 🚀 Atomic Commit Strategy

All pull requests and feature branches must be merged into `main` using a **Rebase and Squash** strategy.

### 1. Daily Sync (Rebase)

Avoid merge commits. Stay updated with `main` via rebasing.

```bash
git fetch origin
git rebase origin/main
```

### 2. Preparing for Finalization (Squash)

Before session closure, squash your micro-commits into a single atomic entry.

### Option A: Interactive Rebase (Recommended)

```bash
# N is the number of commits in your task
git rebase -i HEAD~N
# In the editor, keep the first commit as 'pick' and change the rest to 'squash' (or 's')
```

### Option B: Quick Squash

```bash
git reset $(git merge-base main HEAD)
git add .
git commit -m "feat: your feature description [lightrag-xxx]"
```

### 3. Commit Message Standards

Every squashed commit must reference a **Beads Issue ID**.
Format: `<type>(<scope>): <description> [<issue-id>]`

Example: `feat(auth): add JWT validation [lightrag-123]`

---

## 🔒 Enforcement

The **Orchestrator** validates this during the Finalization phase.

- Missing Issue ID → **BLOCKER**
- Multiple commits pending on PR → **BLOCKER**
- Non-linear history (merge commits) → **BLOCKER**

---

## 🔗 Cross-Repository Changes

When a task requires changes to multiple repositories (e.g., primary workspace plus global skills in `~/.gemini`):

1. **Declare Early**: List linked repositories in `task.md` during Initialization.
2. **Auto-Detection**: The Orchestrator will automatically detect changes in global directories (`~/.gemini`, `~/.agent`).
3. **Branch All**: Create feature branches in **all** repositories using the same naming convention.
4. **PR All**: Create pull requests for **all** repositories before Finalization.
5. **Link PRs**: Reference the primary task's Beads Issue ID in all commit messages and PR descriptions.
6. **Infrastructure Issues**: Modifications to global repositories (`~/.gemini`, `~/.agent`) REQUIRE a dedicated Beads issue for the infrastructure change itself.

**Enforcement**: The Orchestrator will validate linked repositories during the Finalization phase.

---

## 🖥️ GitHub UI Merging

When a Pull Request is ready and approved, it must be merged using the **"Squash and merge"** button.

1. **Navigate** to the Pull Request.
2. **Scroll** to the merge section.
3. **Dropdown**: Click the arrow next to the merge button and select **"Squash and merge"**.
4. **Confirm**: Click the green "Squash and merge" button.
5. **Message**: Ensure the commit message follows the Conventional Commits format and includes the Beads Issue ID.

> [!WARNING]
> Never use "Create a merge commit" or "Rebase and merge" in the GitHub UI, as this violates the linear atomic history requirement.
