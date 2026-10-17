---
name: privacy-review
description: Privacy review, GDPR/LGPD compliance, data minimization, and PII protection.
---

# Privacy Review

Enforce privacy-by-design whenever processing Personal Identifiable Information (PII):
- **Data Minimization:** Collect and retain only fields strictly required for the business purpose.
- **Purpose & Retention Bounds:** Define explicit TTL/retention schedules and support user data export/deletion rights (GDPR/LGPD).
- **PII Protection in Transit & Rest:** Mask or redact PII in application logs, analytics payloads, error trackers, and non-production dumps; encrypt sensitive PII at rest.
- **Consent & Legal Escalation:** Flag missing consent flows or cross-border data transfers for product/legal review before release.
