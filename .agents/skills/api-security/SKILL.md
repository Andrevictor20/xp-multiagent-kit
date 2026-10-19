---
name: api-security
version: 1.0.0
description: API security hardening and OWASP API Security Top 10 controls.
author: André Victor
license: MIT
tags: [owasp, api-security, devsecops, injection-defense, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# API Security

Enforce explicit protection against OWASP API Security Top 10 vulnerabilities:
- **Injection (SQL/NoSQL/Command):** Require parameterized queries and safe ORM bindings; ban raw string interpolation.
- **XSS & Output Encoding:** Sanitize untrusted inputs and enforce safe DOM/template rendering.
- **SSRF:** Validate target URLs, protocols, and DNS resolution; block internal/metadata CIDRs (`169.254.169.254`, `127.0.0.0/8`, RFC1918).
- **Mass Assignment & Data Exposure:** Bind explicit allowlisted DTO fields on input and serialize only public DTO fields on output.
- **Perimeter Controls:** Enforce strict CORS origins, rate limiting, and bounded pagination limits.
