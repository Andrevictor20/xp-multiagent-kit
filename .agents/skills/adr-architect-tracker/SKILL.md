---
name: adr-architect-tracker
description: MADR 3.0 Architectural Decision Records and architectural drift detection.
---

# ADR Architect Tracker

Govern documentation, traceability, and enforcement of **Architectural Decision Records (ADRs)** using MADR 3.0, linking technical decisions directly to `.agents/memory/PROJECT_MEMORY.md`.

## 1. When to Formalize an ADR
Create an ADR whenever a design decision introduces:
1. Adoption or replacement of a technology, framework, or database.
2. Changes to consistency models or async communication (e.g., REST to gRPC/Kafka).
3. Cross-cutting structural patterns (Clean Architecture, Hexagonal, Event Sourcing).
4. Intentional trade-offs impacting security, performance, or operational cost.

## 2. Canonical MADR 3.0 Template (`docs/adr/ADR-NNN-[slug].md`)

```markdown
# ADR-005: Adopt PostgreSQL with pgvector for Semantic Search

- **Status:** Accepted
- **Deciders:** Engineering Team + Antigravity Agent
- **Date:** 2026-09-25

## Context and Problem Statement
Need vector search for documentation chunks under 50ms P95 latency without managing a dedicated vector cluster.

## Considered Options
1. Managed Pinecone
2. Self-Hosted Qdrant
3. PostgreSQL with `pgvector` extension

## Decision Outcome
Chosen Option 3 (`pgvector`) because PostgreSQL already runs in production for transactional data, avoiding extra infrastructure cost and preserving ACID backups.

## Consequences
- **Positive:** Zero extra infra cost; transactional consistency via SQL joins.
- **Negative:** Requires HNSW/IVFFlat index tuning beyond 2M vectors.
```

## 3. Architectural Drift Detection
`navigator` and `refactor-warden` must cross-check active ADRs. Code that contradicts an accepted ADR without a superseding ADR is **blocked at the Quality Gate**.
