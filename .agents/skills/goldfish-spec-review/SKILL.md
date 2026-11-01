---
name: goldfish-spec-review
description: >-
  Blind spec review and stress-testing protocol (Elephant-Goldfish Model).
  Spawns stateless Goldfish subagents with zero conversational history to
  audit design proposals, challenge unbacked assumptions, enforce Heilmeier's
  Catechism, and detect architectural drift.
tags: [architecture, review, spec, atdd, anti-glazing, goldfish]
---

# Goldfish Spec Review Protocol

The **Goldfish Spec Review** implements the *Elephant-Goldfish Model* (EGM) pattern for the XP Multi-Agent Kit.

- **🐘 Elephant (Deep Context)**: The root agent (`orchestrator`) holding full project context, accumulated requirements, and drafting specifications.
- **🐟 Goldfish (Zero Context / Stateless)**: Subagents dispatched with **zero conversational history**. They evaluate the plan as naive or hostile critics to expose unspoken assumptions and blind spots.
- **👤 Human**: Final arbiter deciding trade-offs before code implementation.

---

## 1. Non-Negotiable Principles

1. **Critique First**: Start with fragile, missing, or risky elements before highlighting merits.
2. **Elimination of Sycophancy (No Glazing)**: Prohibited from using empty validation adjectives ("brilliant", "excellent"). Praise without technical proof is noise.
3. **No Echo-Chamber**: Never validate assumptions merely because stated in root prompt. Unproven conclusions are flagged as risks.
4. **Active Stress-Testing**: Answer what the author misses, strongest counter-arguments, and high-load/concurrency failure modes.
5. **No Apologies**: Direct, surgical rationale without token-wasting polite apologies.

---

## 2. Review Phases & Personas

Phases operate in sequence from macro architecture to implementation readiness:
- **Phase 1: Initial Zoom Out** (`personas/zoom_out.md` — Heilmeier Catechism)
- **Phase 2: Plain Language & Comprehension** (`personas/comprehension.md`)
- **Phase 3: Hostile Design Critique** (`personas/design_critic.md` — Concurrency, SPOF, budgets)
- **Phase 4: Intermediate Remediation** (Consolidates `[Blocker]`, `[Major]`, `[Nit]`)
- **Phase 5: Implementation Readiness** (`personas/implementation_readiness.md`)

*See [sections/phases.md](sections/phases.md) for full phase questions and criteria.*

---

## 3. Operational Dispatch (Subagents)

Triggered by invoking a stateless subagent in a clean session:

```python
invoke_subagent(
    TypeName="research",
    Role="Goldfish Design Critic",
    Prompt="""
You are the Goldfish Design Critic (.agents/skills/goldfish-spec-review/personas/design_critic.md).
Audit target document: docs/designs/<specification>.md
Stress assumptions, scalability, cost, and concurrency. Provide zero praise.
"""
)
```

---

## 4. Multi-Pass EGM Engine (`xp-goldfish`)

Execute the 3-pass validator before closing L2/L3 deliveries:
- **Pass 1 (Spec & Readiness):** Heilmeier dimensions, alternatives, file operations table, zero placeholders.
- **Pass 2 (Code Completeness):** Files exist, zero stubs (`NotImplementedError`), zero type bypasses (`as any`).
- **Pass 3 (Conformance Drift):** Confirms 100% of Acceptance Criteria have automated tests via `xp gate check`.
