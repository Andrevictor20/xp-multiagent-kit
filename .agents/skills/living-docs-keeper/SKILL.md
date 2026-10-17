---
name: living-docs-keeper
description: Continuous maintenance of living project documentation and technical decisions.
---

# Living Docs Keeper

Maintain a single authoritative living onboarding document per project (`AGENTS.md`, `CLAUDE.md`, or `.agents/memory/PROJECT_MEMORY.md`) read at the start of every task by human engineers and AI agents.

## 1. Required Living Doc Sections
1. **Architecture Overview:** Core components and communication flows.
2. **Full Tech Stack:** Languages, frameworks, test runners, and external services.
3. **Environment & Config:** Required env vars (names and purpose, never secret values).
4. **Directory Map:** Where services, domain models, jobs, and tests live.
5. **Known Hurdles & Solutions:** Non-obvious pitfalls discovered in practice formatted as `Problem -> Solution` (highest-ROI section).
6. **Design Conventions & Decisions:** Project-wide patterns and ADR summaries.
7. **Recurring Pipelines:** Scheduled jobs, build scripts, and deployment commands.
8. **Post-Implementation Checklist:** Mandatory verification steps before marking tasks done.

## 2. Immediate Update Triggers (Same Work Cycle)
Update living documentation in the **same commit/cycle** whenever:
- A non-obvious hurdle or third-party quirk is solved after investigation.
- An architectural trade-off is decided with the human (`pair-navigator`).
- A new coding convention or module boundary is established.
- A SAST warning is verified as a false positive (`ci-security-gate`).

## 3. Writing Rules
- Write scannable, imperative `Problem -> Solution` bullets (*"Service X blocks non-browser TLS fingerprints -> use headless Chromium with stealth"*), never long narratives.
- Read the living doc before proposing changes so you never rediscover documented hurdles or violate established conventions.

## Checklist
- [ ] Read the living doc before starting the task?
- [ ] Recorded new non-obvious hurdles in `Problem -> Solution` format?
- [ ] Documented architectural decisions with both *what* and *why*?
