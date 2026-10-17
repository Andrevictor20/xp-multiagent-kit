---
name: backend-performance-testing
description: Backend load, stress, spike, and soak testing, profiling, and SLO gates.
---

# Backend Performance & Load Testing Engineering

Empirically validate service scalability, saturation limits, and latency/throughput SLO compliance under concurrent load.

## 1. Canonical Load Test Types

| Test Type | Objective | Load Profile | Target Findings |
| :--- | :--- | :--- | :--- |
| **Smoke** | Sanity check | 1-5 VUs for 1m | Basic functional errors, HTTP 500s |
| **Load** | Expected peak traffic | Peak VUs for 10-30m | P95/P99 SLO violations under sustained load |
| **Stress** | Breaking point discovery | Ramp VUs until failure | Max RPS ceiling, graceful degradation vs. crash |
| **Spike** | Sudden burst resilience | Step jump (0 -> 1000 VUs) | Auto-scaling speed, connection queue recovery |
| **Soak** | Slow leak detection | Moderate VUs for 2h-24h | Heap memory leaks, connection pool exhaustion |

## 2. Critical Backend Bottlenecks
1. **Connection Pool Exhaustion:** DB pool starvation (HikariCP, SQLAlchemy, pgpool) causing acquisition timeouts.
2. **N+1 & Unindexed Queries:** Loop-triggered SQL queries causing linear latency growth with collection size.
3. **Event Loop Lag & Thread Starvation:** CPU-bound synchronous work blocking async runtimes (Node.js, asyncio).
4. **GC Pauses:** Frequent or stop-the-world garbage collection spikes inflating P99 tail latency.

## 3. Mandatory Reliability SLO Gates
1. **Error Rate Gate:** `http_req_failed < 0.1%`.
2. **P95 Latency Gate:** `p(95) < contractual_threshold` (e.g., `< 200ms` for transactional APIs).
3. **P99 Tail Gate:** `p(99) < 2x p(95)_threshold`.

## 4. Declarative k6 Baseline

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<250', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('http://api-service.local/v1/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```
