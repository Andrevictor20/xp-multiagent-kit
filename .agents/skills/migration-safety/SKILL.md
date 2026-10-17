---
name: migration-safety
description: Zero-downtime database migrations using the expand-and-contract pattern.
---

# Migration Safety

Treat "migration ran locally" as distinct from "migration is safe in production":
- **Backward Compatibility:** Every new database migration must remain 100% compatible with the currently running application version during rolling/canary deploys.
- **Strictly Forbidden in a Single Migration:** Adding `NOT NULL` without a default on populated tables, destructive column/table renames, direct `DROP COLUMN`, long table locks (`CREATE INDEX` without `CONCURRENTLY`), or heavy data backfills inside DDL transactions.
- **Expand-and-Contract Pattern:** Split breaking schema changes into (1) Expand (nullable column + dual write), (2) Backfill in batches, (3) Switch reads, and (4) Contract (drop legacy column in a later release).
- **Rollback Plan:** Every migration must include a verified down-migration or an explicit irreversibility mitigation plan.
