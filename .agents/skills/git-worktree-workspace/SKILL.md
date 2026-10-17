---
name: git-worktree-workspace
description: Subagent isolation in clean Git Worktrees via agy-worktree.
---

# Git Worktree Workspace

Isolate subagent execution and high-risk architectural spikes inside dedicated **Git Worktrees** so the developer's main working tree remains clean.

## 1. Why Git Worktrees for Subagents?
- **Total Isolation:** Subagents operate in `.agents/worktrees/<task-name>` on an isolated branch without touching uncommitted work in the main workspace.
- **Instant Failure Rollback:** If a spike or subagent fails verification, destroy the worktree cleanly (`git worktree remove --force`) with zero history pollution.
- **Verified Atomic Merge:** Merge or cherry-pick into the main branch only after `test-guardian` and `release-gatekeeper` confirm 100% GREEN tests.

## 2. Native CLI (`agy-worktree` / `xp-worktree`)

```bash
# 1. Create an isolated worktree for a task
agy-worktree --create auth-oauth-refactor --base main

# 2. List active worktrees
agy-worktree --list

# 3. Remove worktree and delete its branch after merge or abort
agy-worktree --remove auth-oauth-refactor

# 4. Prune all orphan worktrees under .agents/worktrees/
agy-worktree --clean-all
```

## 3. Subagent Delegation Protocol
1. **`orchestrator`** creates the worktree (or invokes subagent with `Workspace="share"` / `"branch"`).
2. Subagent executes the full TDD cycle (`RED -> GREEN -> REFACTOR`) inside the isolated worktree.
3. **`test-guardian`** verifies test evidence; **`builder`** or **`orchestrator`** merges into the target branch.
4. **`archivist`** runs `agy-worktree --remove <task>` to keep the repository clean.
