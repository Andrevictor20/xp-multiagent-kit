---
name: authentication-security
description: Authentication auditing: password hashing, JWT validation, sessions, MFA.
---

# Authentication Security

Audit all authentication flows against strict cryptographic and session controls:
- **Password Hashing:** Use memory-hard algorithms (`Argon2id` or `bcrypt` with work factor >= 12); never use plain SHA/MD5.
- **Brute-Force Defense:** Enforce rate limiting, progressive delays, and credential-stuffing protection on login/MFA endpoints.
- **Session & Token Lifecycle:** Short-lived access tokens, rotating refresh tokens with reuse detection, and server-side revocation on logout/password change.
- **Password Reset & Enumeration:** Use single-use, time-bound cryptographic reset tokens (`<= 15m`) and return identical responses + timing for existing/non-existing accounts.
- **JWT & Cookie Hardening:** Enforce explicit `alg` allowlists (prevent `none` / RS256-to-HS256 confusion), validate `iss`/`aud`/`exp`, and set `HttpOnly; Secure; SameSite=Lax|Strict` on session cookies.
