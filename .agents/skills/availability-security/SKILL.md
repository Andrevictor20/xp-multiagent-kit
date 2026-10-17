---
name: availability-security
description: DoS protection, rate limiting, timeouts, and resource exhaustion defense.
---

# Availability Security

Protect application availability against resource exhaustion and abuse:
- **Request Flooding:** Enforce per-IP and per-user/token rate limiting, burst quotas, and concurrency caps on expensive endpoints.
- **Payload & Query Bounds:** Enforce strict request body size limits, JSON depth limits, mandatory pagination caps (`limit <= 100`), and ReDoS-safe regular expressions.
- **App DoS vs. Infra DDoS:** Combine application-level throttling, queue backpressure, and strict I/O timeouts with edge WAF/CDN and autoscaling controls.
