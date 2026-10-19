---
name: task-routing
description: Risk-based task routing (L0-L3) and surface-to-skill capability mapping.
---

# Task Routing & Capability Routing

Route tasks using the deterministic pipeline `TASK -> RISK (L0-L3) -> SURFACE -> CAPABILITIES -> AGENTS & SKILLS` using the minimum number of agents and turns required.

## 1. Classification Pipeline
0. **Step 0 — Fast Context Bootstrap:** Read `.agents/memory/PROJECT_MEMORY.md` in Turn 1 (< 2k tokens).
1. **Risk Level Inference:**
   - **L0 (Trivial):** Typos, docs, minor CSS (<= 3 turns; code tests exempt).
   - **L1 (Small):** Isolated bugfix or refactor (<= 8 turns; targeted module tests).
   - **L2 (Feature):** New feature/API (<= 20 turns; Specification Pyramid + **⏸️ Stop Gate** + Conformance Report).
   - **L3 (Critical):** Auth, payments, migrations, infra (STRIDE Threat Model + **⏸️ Stop Gate** + full suite + Zero-Downtime Plan).
2. **Surface Detection & Minimum Routing:** Activate only the agents and skills matching the touched surface; never over-route.

## 2. Canonical Domain & Surface Map

```yaml
frontend:
  agents: [designer, builder]
  skills: [frontend-taste-engineering, design-intelligence, mobile-app-design, visual-direction-studio, conversion-copywriting, cro-landing-pages, seo-content-engine, marketing-psychology, copy-editing-sweeps, minimalist-ui, industrial-brutalist-ui, high-end-visual-design, redesign-ui-audit, image-to-code, accessibility-engineering, responsive-architecture, visual-regression, frontend-performance, ui-quality-gate]

design-system:
  agents: [designer]
  skills: [design-tokens, component-architecture, component-registry, design-system-architecture, ui-quality-gate]

debugging-and-root-cause:
  agents: [test-guardian, builder]
  skills: [systematic-debugging, no-workarounds, tdd-safety-net, test-evidence-walkthrough]

code-review-and-deslop:
  agents: [refactor-warden, release-gatekeeper, builder]
  skills: [code-deslop-review, diff-simplifier-review, no-workarounds, atomic-commit-discipline, ci-security-gate]

devops-and-deployment:
  agents: [shipper, release-gatekeeper]
  skills: [zero-downtime-deployment, deploy-pipeline-conductor, observability-and-slo-engineering, ci-security-gate, ci-auto-heal]

infrastructure-as-code:
  agents: [sentinel, shipper]
  skills: [infrastructure-as-code-governance, cloud-security-and-zero-trust, container-security]

api-and-backend:
  agents: [navigator, test-guardian, builder]
  skills: [api-contracts, api-security, database-architecture, migration-safety, caching-architecture, async-messaging-and-resilience, backend-performance-testing]

security:
  agents: [sentinel]
  skills: [threat-modeling, security-sentinel-review, cloud-security-and-zero-trust, api-security, authentication-security, authorization-security, availability-security, security-testing, secrets-guardian, crypto-guardian, container-security, supply-chain-security, privacy-review]

memory-and-docs:
  agents: [archivist]
  skills: [project-memory, living-docs-keeper, lesson-learned, adr-architect-tracker]
```
