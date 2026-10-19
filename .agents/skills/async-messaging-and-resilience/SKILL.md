---
name: async-messaging-and-resilience
version: 1.0.0
description: Async messaging, EDA, Outbox Pattern, DLQ, idempotency, and Circuit Breaker.
author: André Victor
license: MIT
tags: [eda, kafka, rabbitmq, outbox-pattern, circuit-breaker, resilience, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Async Messaging & System Resilience

Ensure zero-loss eventual consistency and fault tolerance across distributed event-driven architectures (EDA).

## 1. Reliable Messaging Patterns

### 1.A Transactional Outbox Pattern
- **Rule:** Never publish directly to a message broker (Kafka, RabbitMQ, SQS) inside a database transaction.
- **Implementation:**
  1. Insert the domain event into a local `outbox` table within the **same ACID transaction** as the business state mutation.
  2. A background relay or CDC worker (e.g., Debezium) polls `outbox` and publishes to the broker (*at-least-once delivery*).
  3. Mark the outbox row processed or delete it only after broker ACK.

### 1.B Consumer Idempotency (Deduplication)
- **Rule:** Distributed brokers deliver *at-least-once*; every consumer must be strictly idempotent.
- **Implementation:**
  - Extract a unique `message_id` or business `idempotency_key`.
  - Check `processed_messages` before executing side effects.
  - Record the key and execute business mutations in the same atomic transaction; if already processed, ACK and drop immediately.

### 1.C Dead Letter Queue (DLQ) & Poison Pill Isolation
- On consumer failure:
  1. Retry up to **N times with exponential backoff** (e.g., 3-5 attempts).
  2. Route unrecoverable messages (*poison pills*) to a **DLQ** with original payload, error stack trace, and retry metadata.
  3. ACK the main queue so processing never stalls, and alert operations on DLQ growth.

## 2. Communication Resilience Patterns

### 2.A Circuit Breaker
Prevent cascading failures when downstream dependencies degrade:
- **Closed:** Normal execution; tracks error rate.
- **Open:** Trips when failure/timeout rate exceeds threshold (e.g., 50% over 10s); fails fast without network calls.
- **Half-Open:** After sleep window (e.g., 30s), allows probe requests; closes on success or re-opens on failure.

### 2.B Exponential Backoff with Full Jitter
Always add jitter to retries to prevent *thundering herd* spikes:
```text
sleep = random(0, min(max_backoff, base_backoff * (2 ^ attempt)))
```
Never use immediate or fixed-interval retries under concurrency.

### 2.C Bulkhead & Backpressure
- **Bulkhead:** Isolate connection and thread pools per external dependency so one slow service cannot exhaust the host.
- **Backpressure:** Use pull-based consumption with bounded prefetch limits.
