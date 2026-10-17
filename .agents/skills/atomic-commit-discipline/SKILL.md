---
name: atomic-commit-discipline
description: Atomic, categorized, CI-verified commits and token-efficient Git ops.
---

# Atomic Commit Discipline

## Golden Rule
**Every commit on the main branch must pass the full CI pipeline and be immediately deployable.** Never push a broken commit intending to "fix it in the next commit".

## Commit Size & Scope
- **One Commit = One Cohesive Change:** A small feature, bugfix, isolated refactor, or config update. Never mix unrelated concerns (e.g., large refactor + new feature) in a single commit.
- Split multi-concern changes into sequential, independently verifiable commits.
- Prefer frequent small commits over monolithic end-of-day merges.

## Conventional Commits Format
Use `<type>(<optional-scope>): <concise imperative summary>`:

| Prefix | Usage |
|---|---|
| `feat:` | New feature (e.g., `feat(api): add invoice export endpoint`) |
| `fix:` | Bug fix |
| `refactor:` | Code restructuring without behavior change |
| `perf:` | Performance optimization |
| `test:` | Adding or updating tests only |
| `docs:` | Documentation-only changes |
| `chore:` | Config, linting, or dependency maintenance |
| `build:` / `ci:` | CI/CD pipeline, build scripts, or infra changes |

Write specific messages that explain *what* changed without opening the diff; ban vague messages like `"updates"` or `"fixes"`.

## Pre-Commit Verification Checklist
1. Passes full CI gate (lint, security scan, test suite — see `ci-security-gate`).
2. Uses accurate Conventional Commit prefix.
3. Leaves zero broken or skipped tests.
4. Decomposes large changes into small sequential commits.

## Token-Efficient Git Operations (< 1.0k tokens)
- **Status:** `git status -s` or `agy-git-ops status` (~50 tokens).
- **Diff Inspection:** `git diff --stat` or `agy-git-ops diff`; inspect specific file diffs via `agy-compact --diff`.
- **History:** `git log -n 5 --oneline` or `agy-git-ops log`.
- **Commit Summary:** `git show --stat <hash>` instead of full `git show`.
- **Push:** `git push --quiet` or `agy-git-ops push`.

## Repository Health Audit Metrics
When auditing commit history, report:
- **Category distribution (%):** Healthy production repos balance `feat` (~40-50%) with `fix`, `refactor`, `test`, `ci`, and `docs`.
- **Throughput cadence:** Steady small releases vs. burst-then-silence monoliths.
- **Emergency refactors:** Massive single-commit file splits following unchecked God-file growth (see `refactor-watchdog`).
