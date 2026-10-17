---
name: deploy-pipeline-conductor
description: Continuous deployment (CD) pipelines, staging promotion, health checks, rollback.
---

# Deploy Pipeline Conductor

Ensure every commit approved by `release-gatekeeper` reaches production through a repeatable, observable, and instantly reversible Continuous Deployment (CD) pipeline.

## 1. Minimum CD Pipeline Stages
1. **Reproducible Artifact Build:** Build a versioned, immutable deployment artifact (multi-stage non-root Docker image or static bundle) from a commit that already passed `ci-security-gate`.
2. **Environment Promotion:** Deploy to `staging` before `production` whenever staging exists. Never skip staging for "small changes".
3. **Automated Post-Deploy Health Check:** Verify `/health` readiness and smoke tests automatically before marking deployment successful.
4. **Deterministic Rollback Path:** Maintain a 1-command automated rollback job (redeploy previous image tag or revert release) that completes in minutes, not manual runbooks.

## 2. Environment Configuration & Secrets
- **Zero Hardcoded Secrets:** Never commit credentials or `.env` files to Git.
- **Strict Environment Isolation:** Keep dev, staging, and production secrets strictly separated.
- **Living Documentation:** Document every new required environment variable (name, purpose, where provisioned) in project docs without exposing secret values.

## 3. High-Risk Feature Rollouts
- Use **feature flags** to decouple code deployment from user activation (instant kill-switch without redeploy).
- Use **gradual rollouts** (canary % traffic) for payment integrations, schema changes, or high-traffic paths.

## 4. Pre-Production Deployment Checklist
- [ ] Artifact built from a commit validated by `release-gatekeeper` and `ci-security-gate`?
- [ ] Verified in `staging` with observed evidence?
- [ ] Automated post-deploy `/health` check configured and passing?
- [ ] Tested rollback job ready?
- [ ] Target environment variables provisioned with zero secrets in repo?
- [ ] Feature flag or canary rollout applied if high-risk (L2/L3)?

## 5. Reference Assets (`assets/`)
- `assets/cd.yml`: GitHub Actions workflow triggered after CI passes (`workflow_run`): builds/pushes Docker image -> deploys to staging + `/health` check -> awaits `production` environment approval -> deploys to production + `/health` check -> provides manual rollback job.
- `assets/Dockerfile` / `assets/Dockerfile.example`: Multi-stage build, non-root user, built-in `HEALTHCHECK` hitting `/health`.
- `assets/docker-compose.dev.yml`: Local development stack only.
