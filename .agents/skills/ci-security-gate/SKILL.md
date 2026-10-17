---
name: ci-security-gate
description: Mandatory CI pipeline gate with linting, dependency audit, SAST, and tests.
---

# CI & Security Gate

## Mandatory Pipeline on Every Commit
1. **Lint & Style:** Enforce formatting and static lint rules (Ruff, ESLint, RuboCop, golangci-lint).
2. **Dependency Audit (SCA):** Scan lockfiles for known CVEs (`npm audit`, `pip-audit`, `bundle-audit`, `trivy`).
3. **Static Application Security Testing (SAST):** Scan code for injection, path traversal, open redirects, and SSRF (Semgrep, Bandit, Brakeman, CodeQL).
4. **Automated Test Suite:** Execute full verification suite (`tdd-safety-net`).

Configure all four jobs as **required status checks** on branch protection rules.

## Proactive Security Habit
Fix security findings in the **same commit** they appear. Proactively harden these surfaces whenever touched:
- **Untrusted User Input:** Strict schema validation, sanitization, parameterized queries.
- **User-Supplied URLs/Hosts:** SSRF allowlisting and internal CIDR blocking.
- **File Uploads & Paths:** Normalize paths and enforce storage outside webroot to prevent path traversal.
- **High-Frequency Public Endpoints:** Rate limiting on login, password reset, and public forms.
- **Sensitive Data at Rest:** Field-level or volume encryption where required.
- **Redirect Parameters:** Allowlist relative paths or trusted domains to prevent open redirects.

If a SAST warning is a verified false positive, document the rationale in code and living docs (`living-docs-keeper`) rather than suppressing blindly.

## Pre-Merge Checklist
- [ ] Linter passes with zero warnings/errors?
- [ ] Zero unmitigated high/critical dependency CVEs?
- [ ] SAST clean (or false positives explicitly documented)?
- [ ] Test suite passes?
- [ ] Sensitive surfaces protected?

## Reference GitHub Actions Asset
Use `assets/ci.yml` as the baseline multi-job pipeline (lint -> dependency audit -> SAST -> test -> container build verification). Adapt package manager and stack commands as needed.
