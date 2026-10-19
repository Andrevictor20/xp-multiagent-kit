---
name: database-architecture
version: 1.0.0
description: SQL/NoSQL schema modeling, indexing, ACID concurrency, and N+1 prevention.
author: André Victor
license: MIT
tags: [database, sql, nosql, indexing, acid, high-scale, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Database Architecture

Validate structural data-layer changes before implementation:
- **Schema Integrity:** Enforce explicit foreign keys, `NOT NULL` constraints, `UNIQUE` indexes, and `CHECK` invariants; balance normalization vs. read-optimized denormalization deliberately.
- **Concurrency & Locking:** Choose appropriate transaction isolation levels, optimistic (`version` column) or pessimistic (`SELECT ... FOR UPDATE`) locking for financial/inventory mutations.
- **Query Performance:** Index foreign keys and filter/sort columns, eliminate N+1 queries via eager loading/joins, inspect `EXPLAIN ANALYZE` plans, and use cursor/keyset pagination on large tables.
- **Safe ORM & Pooling:** Use parameterized queries only, configure bounded connection pools with timeouts, and define data retention/archival policies.
