---
name: caching-architecture
description: Redis/Memcached caching, Cache-Aside, and stampede/avalanche/penetration defense.
---

# Caching Architecture & Invalidation Strategies

Accelerate reads and shield databases/I/O while preserving cache coherence and preventing saturation anomalies.

## 1. Cache Access Patterns

### 1.A Cache-Aside (Lazy Loading — Recommended)
- **Read:** Check cache key (e.g., `user:1001`) -> return immediately on **Hit** -> on **Miss**, query source of truth, set cache with TTL, and return.
- **Write:** Mutate database first, then **delete (invalidate)** the cache key rather than overwriting it to avoid concurrent write race conditions.

### 1.B Write-Through vs. Write-Behind
- **Write-Through:** Synchronously write to cache and DB (immediate consistency, higher write latency).
- **Write-Behind:** Write to cache immediately and batch/queue DB persistence asynchronously (high write throughput, requires durability safeguards).

## 2. Mitigating the 3 Critical Cache Anomalies

### 2.A Cache Stampede (Dog-Piling / Thundering Herd)
- **Cause:** A hot key expires and hundreds of concurrent requests miss simultaneously, overwhelming the DB.
- **Mitigation:**
  1. **Distributed Mutex / Singleflight:** Only one worker recomputes the value while concurrent callers wait briefly or serve slightly stale data (`stale-while-revalidate`).
  2. **Probabilistic Early Expiration (XFetch):** Recompute in background before TTL expiry when `compute_time * beta * ln(random()) > (expiry - now)`.

### 2.B Cache Avalanche
- **Cause:** Massive batches of keys expire at the exact same second.
- **Mitigation:** Add mandatory random **TTL Jitter**:
  ```text
  effective_ttl = base_ttl + random(-delta, +delta)
  ```

### 2.C Cache Penetration
- **Cause:** Queries for non-existent IDs bypass the cache on every request and hit the DB.
- **Mitigation:**
  1. **Null-Value Caching:** Cache `null`/sentinel entries with a short TTL (`30-60s`).
  2. **Bloom Filter:** Reject known non-existent keys at the edge before querying cache or DB.

## 3. Key Naming & Safe Invalidation
- **Semantic Key Namespace:** `<env>:<service>:<entity>:<id>:<version>` (e.g., `prod:billing:invoice:98712:v1`).
- **Event-Driven Invalidation:** Trigger `DEL` via domain events (`InvoiceUpdated`).
- **Schema Versioning:** Bump key version suffix (`:v2`) instead of running blocking `FLUSHALL` or `KEYS *` in production.
