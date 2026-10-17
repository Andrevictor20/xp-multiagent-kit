---
name: zero-downtime-deployment
description: Zero-downtime deployment (Blue/Green, Canary, Rolling) and automated rollback.
---

# Zero-Downtime Deployment & Automated Rollback

Deliver new releases to production with **zero user-facing interruption** using progressive traffic shifting, backward-compatible contracts, and instant automated rollback triggers.

## 1. The 3 Canonical Deployment Strategies

### 1.A Blue/Green Deployment
- Provision and smoke-test the new version (**Green**) in isolation while **Blue** serves 100% of live traffic.
- Switch router/load-balancer traffic atomically to **Green** once smoke tests pass; keep **Blue** warm for instant 1-click rollback.

### 1.B Progressive Canary Release
Shift live traffic in automated, telemetry-gated stages:
1. **Stage 1 (`1% - 5%` for 5-10m):** Monitor RED metrics (*Rate, Errors, Duration*).
2. **Stage 2 (`10% - 25%` for 15m):** Verify HTTP 5xx rate and CPU/memory stability.
3. **Stage 3 (`50%` for 15m):** Validate `p95`/`p99` tail latency under load.
4. **Stage 4 (`100%`):** Complete promotion and retire old replicas.

### 1.C Kubernetes / Container Rolling Updates
- **Mandatory Probes:** Configure `startupProbe` (warmup), `readinessProbe` (gate traffic until DB/cache pools are ready), and `livenessProbe` (restart deadlocked processes).
- **Graceful Shutdown (`SIGTERM`):** Stop accepting new requests on `SIGTERM`, drain in-flight requests (`15-30s`), and close DB connections cleanly before exit.

## 2. Expand-and-Contract Compatibility (DB & APIs)
1. **Phase 1 (Expand):** Add nullable/default DB columns and new API fields/endpoints while keeping legacy contracts active.
2. **Phase 2 (Dual-Write / Migrate):** Deploy application code that writes to both old and new structures and backfills data safely.
3. **Phase 3 (Contract):** Remove legacy columns/endpoints only after 100% of traffic runs stably on the new version.

## 3. Instant Automated Rollback Playbook

### Immediate Abort & Rollback Triggers
- **HTTP 5xx Error Rate:** `> 1%` sustained for `> 2 minutes`.
- **Tail Latency Spike:** `p99` latency increases `> 50%` over baseline.
- **Health Check Failure:** 3 consecutive `readinessProbe` failures.
- **Crash Loop:** Unhandled panic/exception spike.

### Rollback Execution
1. Revert traffic routing immediately (`kubectl rollout undo` or Blue/Green router switch).
2. Preserve failing container logs and traces for `systematic-debugging`.
3. Record incident timeline and root cause in `PROJECT_MEMORY.md` (`lesson-learned`).
