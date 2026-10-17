---
name: systematic-debugging
description: 4-phase scientific debugging, backward tracing, and the 3-Fix Circuit Breaker.
---

# Systematic Debugging: 4-Phase Root-Cause Investigation

> **Iron Law of Debugging:** `NO CODE FIX IS PERMITTED BEFORE ROOT-CAUSE INVESTIGATION.` Guessing and patching symptoms wastes tokens and spawns new bugs.

## 1. The 4 Mandatory Sequential Phases
```text
Phase 1: Root-Cause Investigation -> Phase 2: Pattern Comparison -> Phase 3: Single Hypothesis Test -> Phase 4: TDD Regression Fix
```

### Phase 1: Root-Cause Investigation (Before Touching Code)
1. **Read Full Error Output:** Inspect exact stack trace lines, error codes, and file paths without skimming.
2. **Deterministic Reproduction:** Isolate the exact steps or input that trigger the failure 100% reliably.
3. **Recent Change Check:** Inspect `git status -s` and `git diff --stat` for recent code, config, or dependency changes.
4. **Backward Data Tracing:** Trace corrupted state or invalid values backward through the call chain to the **origin source**, not where the crash surfaced.

### Phase 2: Pattern Analysis & Comparison
1. Locate a working reference flow in the same codebase.
2. Diff every assumption, parameter, and lifecycle step between the working flow and the broken flow.

### Phase 3: Scientific Hypothesis & Minimal Probe
1. **State One Explicit Hypothesis:** *"The root cause is X because Y."*
2. **Test One Variable at a Time:** Apply the smallest possible diagnostic probe to confirm or refute the hypothesis. If refuted, discard cleanly and formulate a new hypothesis — never stack unverified patches.

### Phase 4: TDD Implementation & The 3-Fix Rule
1. **Write a Failing Regression Test (RED):** Reproduce the exact bug in an automated test first.
2. **Fix the Root Cause (GREEN):** Resolve the fault at its origin without opportunistic side refactors.
3. **Verify Surgical Suite:** Confirm the new regression test and module suite pass.
4. **THE 3-FIX RULE (Stop & Question Architecture):** If **3 consecutive fix attempts** fail or trigger new regressions, **STOP IMMEDIATELY**. Three failures indicate an architectural flaw or misunderstood contract — escalate and align with the user instead of attempting a 4th blind patch.

## 2. Red Flags (Stop Immediately If You Think This)
- *"Let me tweak this line quickly to see if tests pass."*
- *"I'm not sure why it failed, but this guard fixed it."*
- *"I'll skip the regression test and check manually."*
