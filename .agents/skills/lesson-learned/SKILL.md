---
name: lesson-learned
description: Capture and formalize procedural lessons learned ([L-NNN]) in project memory.
---

# Institutional Lessons Learned: Permanent Procedural Memory

Whenever a non-obvious bug is solved, a library quirk is uncovered, or an infrastructure pitfall is resolved, formalize it immediately as a numbered lesson (`[L-001]..[L-NNN]`) in Procedural Memory.

## 1. Canonical Lesson Learned Structure

```markdown
### 📘 [L-NNN] Clear Title of Problem and Context

- **Context & Symptom:** What failed and how the error manifested.
- **Confirmed Root Cause:** Exact technical mechanism behind the failure (not guesses).
- **Verified Evidence:** Test or command proving the fix.
- **Actionable Rule:** What to ALWAYS do and NEVER do going forward in this repository.
```

## 2. Reference Examples

```markdown
### 📘 [L-001] Infinite Re-Render in useSyncExternalStore Selector
- **Context & Symptom:** Sidebar failed to update on WebSocket state ticks.
- **Confirmed Root Cause:** Selector returned a new array reference on every tick, triggering React bail-out loops.
- **Verified Evidence:** `tests/sidebar-sync.test.ts` passing with stable selector reference.
- **Actionable Rule:** Memoize selectors returning objects/arrays or provide a value equality comparator.

### 📘 [L-002] iOS Safari Viewport Jump with `h-screen`
- **Context & Symptom:** Bottom primary CTA overlapped by dynamic iOS Safari address bar.
- **Confirmed Root Cause:** `100vh` ignores dynamic mobile browser chrome in WebKit.
- **Verified Evidence:** Mobile viewport emulation check.
- **Actionable Rule:** Always use `min-h-[100dvh]` for full-screen heroes and modals; ban `100vh`.
```

## 3. Memory Integration
1. `archivist` appends a 1-2 line `[L-NNN]` entry to **Section 6 (Gotchas, Hurdles & Learned Playbooks)** of `.agents/memory/PROJECT_MEMORY.md`.
2. `orchestrator` loads these rules during **Step 0 (Fast Context Bootstrap)** so future sessions never repeat past mistakes.
