---
name: security-sentinel-review
description: Proactive security architecture review across auth, PII, payments, and inputs.
---

# Security Sentinel Review

Complement automated SAST (`ci-security-gate`) with proactive architectural security review, secret lifecycle auditing, and blast-radius containment.

## 1. Mandatory Activation Triggers
Activate whenever a task touches:
- **Authentication / Authorization:** Login, sessions, JWTs, RBAC/ABAC, resource ownership.
- **Personal Data (PII):** Names, emails, government IDs, health/financial records.
- **Payments & Billing:** Cards, PIX, webhooks, ledger mutations, payouts.
- **File Uploads or User-Supplied URLs:** Path traversal, SSRF, malicious payloads.
- **External Third-Party Integrations:** Outbound user data sharing and webhook verification.

## 2. Review Checklist by Surface
- **Secrets & Credentials:** Zero hardcoded secrets; support zero-downtime key rotation; enforce least-privilege scope per API key.
- **Auth & Object Authorization:** Argon2id/bcrypt password hashing; expiring/revocable sessions; explicit resource-level ownership checks on every ID parameter (prevent BOLA/IDOR).
- **Personal Data (PII):** Collect minimum required fields; support user data deletion; encrypt sensitive fields at rest.
- **Untrusted Input Surfaces:** Block SSRF on server-side URL fetches; normalize file paths and validate MIME/magic bytes; enforce rate limiting on login/reset/public forms.
- **Dependencies & Third Parties:** Verify necessity and CVE posture of new packages (`dependency-governance`).

## 3. Incident Readiness & Verdict Reporting
- Ensure audit logs identify *who* accessed *what* sensitive resource and provide a fast credential/session revocation path.
- Classify findings as `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` with minimal root-cause fixes. **CRITICAL and HIGH findings block release.**
