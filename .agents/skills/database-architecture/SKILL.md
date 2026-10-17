---
name: database-architecture
description: SQL/NoSQL schema modeling, indexing, ACID concurrency, and N+1 prevention.
---

# Database Architecture

Validate structural data-layer changes before implementation:
- **Schema Integrity:** Enforce explicit foreign keys, `NOT NULL` constraints, `UNIQUE` indexes, and `CHECK` invariants; balance normalization vs. read-optimized denormalization deliberately.
- **Concurrency & Locking:** Choose appropriate transaction isolation levels, optimistic (`version` column) or pessimistic (`SELECT ... FOR UPDATE`) locking for financial/inventory mutations.
- **Query Performance:** Index foreign keys and filter/sort columns, eliminate N+1 queries via eager loading/joins, inspect `EXPLAIN ANALYZE` plans, and use cursor/keyset pagination on large tables.
- **Safe ORM & Pooling:** Use parameterized queries only, configure bounded connection pools with timeouts, and define data retention/archival policies.
