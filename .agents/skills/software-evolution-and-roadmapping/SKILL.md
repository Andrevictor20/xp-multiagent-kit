---
name: software-evolution-and-roadmapping
description: Technical roadmapping, Now/Next/Later horizons, Strangler Fig, and RFC 8594.
---

# Software Evolution & Strategic Technical Roadmapping

Connect product and architecture vision to a sustainable 6-24 month evolution plan without "Big Bang" rewrites or EOL obsolescence.

## 1. Dynamic Horizons: Now / Next / Later

| Horizon | Focus | Required Validation |
| :--- | :--- | :--- |
| **NOW (1-4 wks)** | Committed scope, high granularity | Strict ATDD/TDD + Acceptance Criteria |
| **NEXT (1-3 mos)** | Preliminary architecture & validated goals | Preliminary ADRs + technical spikes |
| **LATER (3-12+ mos)** | Strategic scale & structural shifts | Objective transition triggers (metrics) |

## 2. Legacy Modernization: The Strangler Fig Pattern
**Golden Rule:** Never approve from-scratch Big Bang rewrites. Migrate incrementally:
1. **Edge Interception:** Place an API Gateway / reverse proxy (Nginx, Envoy) in front of the legacy system.
2. **Vertical Slice Extraction:** Extract one bounded domain slice into the new module/service with full TDD and contract tests.
3. **Shadowing & Canary Shift:** Mirror dark traffic to compare responses, then shift traffic gradually (`1% -> 10% -> 50% -> 100%`).
4. **Pruning:** Delete dead legacy code once 100% of traffic runs stably on the new slice.

## 3. Proactive Capacity Planning & FinOps
- **Data Growth:** Project monthly row growth on core tables; plan partitioning, read replicas, or cold archival before tables cross tens of millions of rows.
- **Connection & IOPS Ceilings:** Add `Cache-Aside` or read replicas whenever sustained peak pool/IOPS utilization exceeds **70%**.
- **FinOps:** Audit oversized instances quarterly and commit stable baselines to reserved capacity.

## 4. EOL Governance & API Sunset Policy (RFC 8594)
- **Major Runtime/Framework Upgrades:** Schedule biannual/annual LTS upgrades; treat EOL dependencies as P1 security debt.
- **RFC 8594 API Deprecation:** Emit `Deprecation: @<timestamp>` and `Sunset: <http-date>` headers, provide a 90-180 day migration window, and retire legacy endpoints only when JSON telemetry confirms `0%` residual traffic.
