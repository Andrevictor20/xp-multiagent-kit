---
name: security-observability
description: Real-time security monitoring, audit logging, and PII/secret log redaction.
---

# Security Observability

Instrument infrastructure and application audit trails for security detection and incident response:
- **Security Audit Events:** Log and alert on repeated failed logins, password reset abuse, MFA failures, RBAC/BOLA authorization denials, and rate-limit spikes.
- **Immutable Context:** Include `timestamp`, `actor_id`, `ip`, `user_agent`, `resource_id`, `action`, `outcome`, and `correlation_id` in security events.
- **Strict Redaction:** **NEVER log plaintext passwords, JWTs, session cookies, API keys, or raw payment/PII fields.**
