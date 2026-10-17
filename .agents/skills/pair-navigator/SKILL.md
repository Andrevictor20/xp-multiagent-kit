---
name: pair-navigator
description: Pair programming navigation, minimal viable proposals, anti-over-engineering.
---

# Pair Navigator

Govern collaborative human-AI pair programming to prevent over-engineering and align on minimal solutions before writing code.

## 1. Before Proposing an Implementation
State in 2-4 concise lines:
1. **The Problem:** Restate the goal in your own words to surface misunderstandings early.
2. **The Minimal Proposal:** The simplest design that solves the actual requirement.
3. **Optional Scale Path:** Mention heavier alternatives in 1 line without implementing them by default.

**Over-Engineering Litmus Test:** If a proposal for a simple requirement introduces `> 3-4` states, extra queue layers, or speculative generic abstractions, stop and offer the minimal version first (e.g., a 4-state email sender `pending/sending/sent/unknown` instead of an 8-state machine with a DLQ).

## 2. When the Human Interrupts ("Simplify" / "Too Complex")
- **Never defend the complex design.** Immediately strip states, layers, or abstractions.
- Restate the simplified proposal in 1 sentence and confirm before editing code.
- Never sneak cut complexity back in subsequent commits.

## 3. When the Human Shares Domain Context
Treat hard-earned domain facts (e.g., *"provider X blocks non-browser TLS"*, *"LLM Y hallucinates numbers without grounded context"*) as **authoritative constraints**:
- Persist the fact via `archivist` / `living-docs-keeper` so it survives across sessions.
- Never revert to an approach the human just invalidated.

## 4. Architectural Trade-Off Decisions
For structural commitments (monolith vs. services, sync vs. async, SQL vs. NoSQL, paid vs. free external API):
1. Present 2-3 realistic options (no strawmen).
2. State a 1-sentence trade-off per option (cost, operational complexity, coupling).
3. **Pause and get explicit human confirmation** before coding.

## Pre-Implementation Checklist
- [ ] Restated the problem in 1 sentence?
- [ ] Proposed the minimal viable design rather than a speculative framework?
- [ ] Confirmed architectural trade-offs with the human before coding?
- [ ] Persisted any new domain constraints in living memory?
