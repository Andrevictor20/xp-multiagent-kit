---
name: observability-and-slo-engineering
description: Observability engineering: JSON logs, RED metrics, OpenTelemetry tracing, SLOs.
---

# Observability, Telemetry & SLO Engineering

Turn observability into an active reliability engine for rapid incident diagnosis, distributed trace correlation, and SLO error-budget governance.

## 1. The 3 Pillars of Observability

### 1.A Single-Line Structured JSON Logs
Emit all production logs to `stdout` as single-line JSON objects with zero PII (never log passwords, JWTs, credit cards, or secrets):
```json
{
  "timestamp": "2026-08-28T16:10:00.123Z",
  "level": "INFO",
  "service": "billing-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "correlation_id": "req-987654321",
  "user_id": "usr-12345",
  "message": "Payment processed successfully",
  "duration_ms": 142.5
}
```

### 1.B Application Metrics: The RED Pattern
Track for every HTTP/gRPC endpoint and queue consumer:
1. **Rate:** Requests per second (`http_requests_total`).
2. **Errors:** Failing requests (`http_requests_errors_total`, HTTP 5xx).
3. **Duration:** Latency histograms (`p50`, `p90`, `p95`, `p99` via `http_request_duration_seconds_bucket`) plus queue lag.

### 1.C Distributed Tracing (OpenTelemetry)
- Propagate W3C `traceparent` headers across all HTTP calls and async message brokers (Kafka, RabbitMQ, SQS).
- Wrap DB queries, external API calls, and heavy I/O in dedicated spans.

## 2. SLIs, SLOs & Error Budgets
```text
SLI (Measured Metric) -> SLO (Target Threshold) -> Error Budget (Allowed Failure Margin)
```
- **Availability SLI/SLO Example:** `non-5xx requests / total valid requests >= 99.9%` over 30 days (~43m allowed downtime/month).
- **Latency SLI/SLO Example:** `95% of requests < 250ms`.
- **Error Budget Freeze:** If error-budget burn spikes (e.g., 50% burned in 1h), **freeze feature deployments** and prioritize reliability fixes.

## 3. Actionable Alerts & Post-Deploy Window
- **Symptom-Based Paging:** Page on-call engineers only on user-impacting symptoms (Error Budget burn rate, 5xx spike, P99 degradation), never noisy transient CPU blips.
- **Post-Deploy Observation Window:** Actively monitor RED metrics for **5-15 minutes** after every production deploy; trigger immediate rollback on abnormal error or latency spikes.
