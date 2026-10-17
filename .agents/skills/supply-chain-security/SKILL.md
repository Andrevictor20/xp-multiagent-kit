---
name: supply-chain-security
description: Software supply chain security (SCA), lockfile integrity, and anti-typosquatting.
---

# Supply Chain Security

Protect the software supply chain before installing or upgrading external packages:
- **Deterministic Lockfiles:** Commit and enforce lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`) using frozen installs (`npm ci`, `pip install --require-hashes`) in CI.
- **Provenance & Typosquatting Check:** Verify exact package names, publisher reputation, and repository links before installation to prevent dependency confusion and typosquatting.
- **Automated SCA Audits:** Run vulnerability scanners (`npm audit`, `pip-audit`, `trivy fs`) in CI and prefer native stdlib capabilities over micro-dependencies.
