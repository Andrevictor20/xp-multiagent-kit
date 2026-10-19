---
name: secrets-guardian
version: 1.0.0
description: Credential leak prevention across code, .env, Git history, and build artifacts.
author: André Victor
license: MIT
tags: [secrets, security, credentials, devsecops, scanner, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Secrets Guardian

Prevent credentials, API keys, private keys, and tokens from leaking into source code, logs, or artifacts:
- **Scan All Surfaces:** Check source files, `.env*` files, Git commit history, Docker layers, and CI logs.
- **Hard Gate:** `sentinel` and `release-gatekeeper` block any commit containing hardcoded secrets or high-entropy keys.
- **Incident Remediation Flow:** Deleting a leaked line is never enough — execute `detect -> revoke -> rotate -> scrub history -> audit access logs`.
