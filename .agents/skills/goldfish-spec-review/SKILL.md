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

- **🐘 Elephant (Deep Context)**: The root agent (`navigator` or `orchestrator`) holding full project context, accumulated requirements, and drafting the specifications.
- **🐟 Goldfish (Zero Context / Stateless)**: Subagents dispatched via `invoke_subagent` with **zero conversational history**. They receive only the target document and referenced code. Their role is to evaluate the plan as a naive reader or hostile critic to expose unspoken assumptions and blind spots.
- **👤 Human**: The final arbiter who decides trade-offs before releasing code implementation.

---

## 1. Non-Negotiable Principles (Anti-Glazing & Hostile Review)

1. **Critique First**: Even on solid proposals, explicitly start with what is fragile, missing, or risky before highlighting merits.
2. **Elimination of Sycophancy (No Glazing)**:
   - Prohibited from using empty validation adjectives ("brilliant", "excellent", "perfect", "great idea").
   - Praise without technical evidence is noise and masks risk.
3. **Rejection of Echo-Chamber Framing (No Echo-Chamber)**: Never validate an assumption merely because the user or root agent stated it. If a conclusion lacks proof, flag it as an unjustified assumption.
4. **Active Stress-Testing**: For every technical decision, answer:
   - *What is the author not seeing?*
   - *What is the strongest counter-argument?*
   - *How does this solution fail under high load, network partitions, or concurrency?*
5. **Zero Apologies (No Apologies)**: Do not waste tokens apologizing when corrected or challenged. Adjust arguments and state technical rationale directly.

---

## 2. The 5 Phases of the Goldfish Protocol

When auditing an architectural specification (L2/L3) or a PRD:

### Phase 1: Initial Zoom Out Review
* **Persona**: `personas/zoom_out.md`
* **Standard**: `resources/zoom-out-standard.md` (Heilmeier Catechism)
* **Mandatory Questions**:
  - What are we trying to do? (No jargon)
  - How is it done today and what are the limits of current practice?
  - What is new in this approach and why do we think it will succeed?
  - Who cares? If we succeed, what difference does it make?
  - What are the risks and costs (QPS, memory, tokens, latency)?
  - What are the midterm and final exams to check for success?

### Phase 2: Comprehension & Plain Language Review
* **Persona**: `personas/comprehension.md`
* **Criterion**: Can the text be understood without ambiguity by an engineer who just joined the team? Are there promotional buzzwords (*seamless, robust, blazingly fast*)? Are technical mechanisms explained objectively?

### Phase 3: Hostile Design Critique
* **Persona**: `personas/design_critic.md`
* **Focus**:
  - Scalability bottlenecks and single points of failure (SPOF).
  - Resource footprint: peak QPS, storage consumption, and LLM/token budgets.
  - Concurrency inconsistencies, idempotency, and transactional failure handling.

### Phase 4: Intermediate Alignment & Remediation
* The root agent consolidates findings into `[Blocker]`, `[Major]`, and `[Nit]`.
* Fixes gaps in the specification before submitting to Human Gate.

### Phase 5: Implementation Readiness
* **Persona**: `personas/implementation_readiness.md`
* **Standard**: `resources/implementation-readiness-standard.md`
* **Criterion**: Does the development team (`builder` / `test-guardian`) have everything needed to code without guessing behavior? Are acceptance criteria and edge cases 100% bounded?

---

## 3. Operational Dispatch (Subagents)

The orchestrator or `navigator` triggers the review by invoking the subagent in a clean session:

```python
# Invocation via Antigravity / CLI Driver
invoke_subagent(
    TypeName="research",  # or stateless read-only subagent
    Role="Goldfish Design Critic",
    Prompt="""
You are the Goldfish Design Critic. Read the persona at:
.agents/skills/goldfish-spec-review/personas/design_critic.md

Audit the document in REVIEW mode:
TargetFile: docs/designs/<specification>.md
Standard: .agents/skills/goldfish-spec-review/resources/heilmeier-standard.md

Your goal is to stress assumptions and uncover flaws in scalability,
cost, and concurrency. Provide no praise. Be surgical.
"""
)
```

---

## 4. Multi-Pass EGM Automated Engine (`xp-goldfish` / `agy-goldfish`)

In addition to blind review via subagents (`invoke_subagent`), execute the CLI 3-pass validator before closing any L2/L3 delivery:

```bash
# Fast Zero-Decision Readiness check (Pass 1)
xp-goldfish --check-readiness .agents/specs/SPEC-NNN.md

# Complete Multi-Pass audit (Pass 1: Spec + Pass 2: Code Completeness + Pass 3: Spec-vs-Code Drift)
xp-goldfish --multipass .agents/specs/SPEC-NNN.md \
  --code-files src/module.py \
  --test-files tests/test_module.py
```

- **Pass 1 (Spec & Zero-Decision Readiness):** Checks all 6 Heilmeier dimensions, Considered Alternatives, file operations table (`Create`/`Modify`/`Delete`), `AC-N`, Anti-Glazing, and total absence of placeholders (`TODO`, `TBD`, `{{...}}`).
- **Pass 2 (Codebase Details & Completeness):** Verifies all implemented files exist, contain no stubs (`NotImplementedError`), `TODO`/`FIXME`, or type workarounds (`as any`, `@ts-ignore`).
- **Pass 3 (Spec-vs-Code Drift):** Confirms that 100% of `AC-N` have corresponding automated tests.
