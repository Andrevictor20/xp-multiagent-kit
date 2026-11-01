---
name: security-review
description: Comprehensive application security review covering AuthN/AuthZ, OWASP API, container hardening, crypto, secrets, and SAST/DAST testing.
---

# Security Review (`security-review`)

Consolidates application security governance: **AuthN/AuthZ**, **OWASP API**, **Crypto**, **Secrets**, **Containers**, and **Negative Security Testing**.

## 1. Authentication (AuthN) & Authorization (AuthZ)
- **Passwords & Hashing:** Argon2id or bcrypt with calibrated work factor. Absolute ban on MD5/SHA1 for credentials.
- **Tokens & Sessions:** Asymmetric JWT (RS256/ES256) validating `exp`, `iss`, `aud`, and key rotation.
- **Authorization:** Endpoint and row-level RBAC/ABAC (strict prevention of IDOR/BOLA). Multi-tenant isolation enforced via `tenant_id` validated from token.

## 2. OWASP API Security & Resilience
- **Rate Limiting:** Brute-force protection on sensitive routes (`/login`, `/reset-password`).
- **Input Validation:** Strict schemas (Pydantic, Zod) rejecting unexpected properties and injections.
- **Timeouts & DoS:** Explicit timeouts configured across all external HTTP/RPC calls and database queries.

## 3. Cryptography & Secrets Governance
- **Encryption at Rest:** AES-GCM-256 or ChaCha20-Poly1305 with unique IV/Nonce per operation.
- **Secrets Governance:** Never commit secrets, tokens, or passwords in code or `.env`. Mandatory use of KMS or Secret Manager.
- **Secret Scanning:** Pre-commit scanner blocking signatures of API keys, AWS tokens, Stripe keys, etc.

## 4. Container Hardening & Supply Chain (SCA)
- Minimal base images (Distroless or Alpine) running mandatorily under non-root users.
- Dependency vulnerability auditing (`pip audit`, `npm audit`) and lockfile integrity verification against typosquatting.

## 5. Negative Security Testing (SAST/DAST)
- Every authenticated route must have unit and integration tests verifying:
  - Missing token -> HTTP 401.
  - Expired token or invalid signature -> HTTP 401.
  - Attempted access to another user/tenant resource -> HTTP 403 / 404.
