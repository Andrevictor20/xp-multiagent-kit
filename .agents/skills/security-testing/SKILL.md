---
name: security-testing
description: Proactive SAST/DAST and negative security test cases against auth bypass/injection.
---

# Security Testing

Write automated negative and abuse-case security tests in controlled test/staging environments (never against production):
- **Access Control Tests:** Verify unauthenticated requests (`401`), insufficient roles (`403`), cross-tenant/cross-user ID manipulation (BOLA/IDOR), and mass-assignment rejection.
- **Injection & Input Abuse:** Test SQL/NoSQL injection payloads, XSS vectors, SSRF internal IP targets, and path traversal sequences (`../../etc/passwd`).
- **Threat Model Traceability:** Convert every STRIDE threat identified in `threat-modeling` into a reproducible failing security test (**RED**) before implementing the control (**GREEN**).
