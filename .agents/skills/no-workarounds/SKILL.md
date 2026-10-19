---
name: no-workarounds
version: 1.0.0
description: Root-cause fixes only: ban workarounds, type casts, linter suppression, sleeps.
author: André Victor
license: MIT
tags: [clean-code, debugging, code-quality, zero-workarounds, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# No Workarounds: Fix the Source, Never Silence the Signal

> **Principle:** A workaround masks a symptom while leaving the root cause intact. **Fix the source, not the signal.**

## 1. The Pre-Commit Gate
Before committing any fix, verify:
1. Does this change resolve the **root cause** or merely hide the symptom?
2. Am I fixing the underlying contract or silencing the compiler, linter, or test runner?

## 2. The 7 Workaround Signals (Strictly Forbidden)

| Category | Silenced Signal | Root-Cause Fix |
| :--- | :--- | :--- |
| **TYPE** | `as any`, `as unknown as T`, `!` | Fix the type definition or validate external payloads at the boundary via Zod/schemas. |
| **LINT** | `eslint-disable`, `@ts-ignore`, `# noqa` | Fix the unsafe code pattern flagged by the static analyzer. |
| **SWALLOW** | Empty `catch {}`, `.catch(() => null)`, `except: pass` | Handle the error explicitly, log with context, or return a typed `Result`. |
| **TIMING** | `setTimeout`, `sleep(1000)`, fixed retry delays | Fix the race condition using deterministic readiness events or condition polling. |
| **PATCH** | Global prototype mutation or monkey-patching | Use an explicit adapter/wrapper or official extension hook. |
| **SCATTER** | Defensive `?.` and `??` chains everywhere | Validate and normalize data once at the ingestion boundary. |
| **CLONE** | Copy-pasted blocks with minor tweaks | Extract a cohesive shared function or parameterized module. |

## 3. Controlled Escape Hatch (Upstream Third-Party Bugs Only)
A temporary workaround is permitted **ONLY IF ALL 4 CONDITIONS HOLD**:
1. The root cause is proven to live inside an external upstream dependency.
2. An official upstream fix is unavailable or blocked on an external release.
3. Blocking delivery costs more than the isolated technical debt.
4. The workaround is 100% encapsulated in a single adapter.

### Mandatory Containment Procedure
1. Add `// WORKAROUND: [exact reason] - see [upstream issue/PR URL]`.
2. Add a **Canary Test** that fails once the upstream fix lands so the workaround is removed.
3. Log a debt entry in `PROJECT_MEMORY.md` with a max 90-day review deadline.
