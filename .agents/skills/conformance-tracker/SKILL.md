---
name: conformance-tracker
version: 1.0.0
description: Traceability between Acceptance Criteria and tests via Conformance Report.
author: André Victor
license: MIT
tags: [conformance, traceability, acceptance-criteria, testing, cursor, claude-code]
compatibility: [cursor, claude-code, codex, gemini-cli, opencode]
entrypoint: SKILL.md
---

# Conformance Tracker

Enforce 1:1 traceability between human-approved Acceptance Criteria (AC) and automated tests so that **100% passing tests = 100% fulfilled specification contract**.

## 1. Canonical Conformance Report Format

```markdown
## Conformance Report — SPEC-NNN: [Title]

### Summary
- **Total Criteria:** N
- **Covered by Tests:** N/N
- **Passing (GREEN):** N/N
- **Status:** ✅ COMPLIANT | ❌ NON-COMPLIANT

### Traceability Matrix

| # | Acceptance Criteria | SbE Rows | Test File | Test Name | Status |
|---|---|---|---|---|---|
| AC-1 | [description] | 3 examples | `tests/test_x.py` | `test_ac1_valid` | ✅ GREEN |
| AC-2 | [description] | 4 examples | `tests/test_x.py` | `test_ac2_duplicate` | ✅ GREEN |

### Execution Evidence
- **Command:** `python3 -m unittest tests/test_x.py`
- **Exit code:** 0
- **Output:** [concise verified output]
```

## 2. Conformance Rules

### Hard Gates (Block Delivery)
1. **100% AC Coverage:** Every AC must map to at least one automated test. Missing test = `NON-COMPLIANT`.
2. **All GREEN:** Every mapped test must pass. Any failing test = `NON-COMPLIANT`.
3. **Real Native Evidence:** GREEN status must be backed by actual test runner execution (evidence level >= L1). Verbal claims are rejected.

### Soft Gates (Warnings)
1. **SbE Completeness:** Verify all rows in Specification by Example tables are parameterized in tests.
2. **Orphan Tests:** Review tests not linked to any AC for undocumented requirements or redundant testing.

## 3. Activation by Risk Level
- **L0 (Trivial):** Exempt.
- **L1 (Small):** 1-2 line informal summary.
- **L2 (Feature):** Mandatory full Conformance Report.
- **L3 (Critical):** Mandatory full Conformance Report + Threat Model cross-reference.

## 4. Automated CLI Generation
Generate and verify the report deterministically via CLI (exits `1` on `NON-COMPLIANT`):
```bash
agy-conformance --spec docs/specs/SPEC-042.md --tests tests/
```
