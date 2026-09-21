---
name: authentication-security
description: "Auditoria de autenticação, sessões, JWT, MFA e fluxos de login."
---

# Authentication Security

Revise minuciosamente componentes de autenticação:
- Algoritmos fortes de hashing de senha (Argon2id, bcrypt).
- Prevenção a Brute force / Credential stuffing.
- Rotação e expiração de sessão / Refresh tokens.
- Reset de senha seguro, account enumeration.
- Validação estrita de JWT (algorithm confusion) e configurações de Cookie (HttpOnly, Secure, SameSite).
