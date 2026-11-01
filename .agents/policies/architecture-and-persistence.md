# Architecture, Persistence & Platform-Native Policy

## 1. Database Architecture & Concurrency
1. **Explicit Indexing:** Foreign keys and filter/sort predicates must have explicit indexes to prevent full table scans.
2. **N+1 Prevention:** Batch and eager-load relational associations; prohibit unbounded in-loop queries.
3. **Transaction Boundaries:** Enforce atomic boundaries around multi-step state mutations; handle rollback gracefully on errors.
4. **Expand-and-Contract Migrations:** Schema changes must follow two-phase expand-and-contract patterns to ensure zero downtime.

## 2. Platform-Native First (Zero Unnecessary Dependencies)
Before adding third-party dependencies, exhaust native platform primitives:
- **HTML/DOM:** Native `<dialog>`, `<details>/<summary>`, `<datalist>`, Popover API, native form constraints.
- **CSS:** CSS Grid/Subgrid, Container Queries (`@container`), `:has()`, CSS Nesting, View Transitions, `clamp()`.
- **Web/JS APIs:** `fetch`, `AbortController`, `structuredClone`, `Intl.*`, `crypto.randomUUID()`, `IntersectionObserver`, `URLSearchParams`.
- **Python Stdlib:** `pathlib`, `dataclasses`, `unittest`, `sqlite3`, `urllib.request`, `concurrent.futures`, `functools.lru_cache`.
