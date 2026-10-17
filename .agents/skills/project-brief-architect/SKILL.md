---
name: project-brief-architect
description: Zero-Moment technical interview and structured project brief for Genesis.
---

# Project Brief Architect

Conduct a focused senior-engineer discovery interview at **Moment Zero** (before any code or scaffold exists) to turn vague project requests into an actionable brief for `genesis`.

## 1. Full vs. Partial Interview Rules
- **Never repeat answered questions:** Confirm what the user already specified in 1 sentence and ask only about missing architectural gaps.
- **Batch 2-3 questions max per turn:** Keep it conversational. Prioritize architecture-shaping decisions (scope, stack, persistence, auth) before secondary details.
- **State explicit defaults:** When assuming a sensible default (e.g., Docker setup), state it clearly so the user can override it.

## 2. The 9 Discovery Categories
1. **Scope & MVP Features:** Day-1 core features vs. Phase-2 nice-to-haves; identify complexity anchors (e.g., payments, real-time sync).
2. **Tech Stack:** Preferred language/framework, monorepo vs. split frontend/backend, package manager/runtime (`pnpm`, `bun`, `uv`, `poetry`).
3. **Data Persistence:** Relational SQL, NoSQL document store, or stateless/file-backed; expected initial data volume.
4. **Authentication & Authorization:** Public vs. login required; email/password vs. OAuth (Google/GitHub); RBAC roles (user vs. admin).
5. **Containerization:** Docker + `docker-compose.dev.yml` vs. native local runtime.
6. **Deployment & Hosting:** Target platform (Vercel, Fly.io, Render, AWS, VPS) and environments (`staging + production` vs. `production` only).
7. **External Integrations:** Payments (Stripe/PIX), transactional email, object storage (S3/R2), third-party APIs/webhooks.
8. **Non-Functional Requirements:** Expected user scale and compliance/PII constraints (LGPD/GDPR, health/financial data).
9. **Team & Timeline Context:** Solo vs. multi-contributor repo; tight deadline vs. long-term evolution.

## 3. Output Format: Structured Genesis Brief
Synthesize the confirmed answers into this exact block and get user confirmation before invoking `genesis`:

```text
PROJECT: <1-line name and description>

FEATURES (MVP):
- <feature 1>
- <feature 2>

FEATURES (Phase 2 - out of scope for now):
- <deferred feature 1>

STACK:
- Language/Framework: <...>
- Package Manager: <...>
- Persistence: <database or "none">

AUTHENTICATION: <yes/no - method and roles>
CONTAINERIZATION: <Docker yes/no>

DEPLOY:
- Target Platform: <...>
- Environments: <staging + production | production only>

EXTERNAL INTEGRATIONS: <list or "none">
NON-FUNCTIONAL REQUIREMENTS: <scale, compliance/PII>
CONTEXT: <solo/team, timeline>
```
