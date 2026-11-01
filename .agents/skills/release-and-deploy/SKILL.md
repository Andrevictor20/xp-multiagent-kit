---
name: release-and-deploy
description: End-to-end continuous deployment, CI security gates, dependency governance, observability/SLOs, and zero-downtime release strategies.
---

# Release and Deploy (`release-and-deploy`)

Consolidates disciplines of **CI/CD**, **Release Gates**, **Dependency Governance**, **Observability**, and **Zero-Downtime Deployment**.

## 1. CI (Continuous Integration) Gates
- Automated pipelines with sequential execution: Lint -> Audit -> SAST -> Unit Tests -> Integration Tests.
- Failure at any step immediately blocks release progression.

## 2. Dependency Governance & Licensing
- Evaluation of third-party dependencies against bloat and incompatible restrictive licenses.
- Strict lockfiles with pinned SHA-256 hashes in version control.

## 3. Zero-Downtime Deployment Strategies
- **Canary & Blue/Green:** Gradual traffic promotion (10% -> 50% -> 100%) monitoring error rates.
- **Automated Instant Rollback:** If HTTP 5xx error rate or p99 latency breaches SLO thresholds during rollout, immediately abort and revert.

## 4. Observability & RED/SLO Metrics
- Structured JSON logging with mandatory fields: `timestamp`, `level`, `trace_id`, `service`, `message`.
- Continuous tracking of RED metrics (Rate, Errors, Duration) and availability SLIs/SLOs.
