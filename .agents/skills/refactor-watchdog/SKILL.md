---
name: refactor-watchdog
description: Continuous refactoring watchdog against duplication and God files (>500 lines).
---

# Refactor Watchdog

Proactively detect and propose small, continuous refactorings during regular delivery before code spirals into unmaintainable God files.

## 1. Triggers to Propose Immediate Refactoring
1. **Real Logic Duplication (Rule of 2):** The same business or control-flow pattern appears in 2+ places. Extract on the second occurrence.
2. **Mixed Responsibilities:** A module cannot be summarized in one sentence without using "and" multiple times.
3. **Monotonic File Growth:** A file grows on every commit and never shrinks.
4. **Line-Count Ceiling:** Flag any production file approaching **500 lines** (hard kit limit; >800 lines requires immediate modular split before adding features).

## 2. How to Execute Continuous Refactoring
- Keep refactorings **small, fast, and isolated** in their own `refactor:` commit (`atomic-commit-discipline`).
- Verify `tdd-safety-net` test coverage **before** moving code; refactoring without green tests is an unsafe rewrite.
- Name extractions clearly (e.g., `Extract retry policy wrapper`, `Split token formatter from tracker`).

## 3. Anti-Pattern to Prevent: "Build-Build-Build-Emergency-Surgery"
Unchecked growth where a single file balloons 10x across dozens of commits (e.g., 500 -> 5,000 lines) forces high-risk emergency multi-file splits and cuts commit throughput by >60%. Halt feature additions and propose a modular split as soon as a file approaches the 500-line ceiling.

## Pre-Edit Checklist
- [ ] Is the target file approaching 500 lines and needing a split before adding new logic?
- [ ] Does similar logic already exist elsewhere in the repo to consolidate?
- [ ] Are behavior tests GREEN before moving or extracting code?
- [ ] Can the refactor land as a small, isolated `refactor:` commit?
