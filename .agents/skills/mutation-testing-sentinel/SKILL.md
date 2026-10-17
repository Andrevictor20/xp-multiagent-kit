---
name: mutation-testing-sentinel
description: Test suite robustness auditing via mutation injection and >=80% mutation score.
---

# Mutation Testing Sentinel

Verify that automated tests actually catch regressions by injecting controlled code mutations (Mutation Testing) to eliminate tautological assertions and false-positive suites.

## 1. Core Principles & Threshold
100% line coverage does not prove test quality if tests still pass when operators (`>` to `<=`, `true` to `false`) or statements are mutated.
- **Killed Mutant:** A test fails immediately when the mutation is injected (robust test).
- **Surviving Mutant:** All tests still pass despite mutated production logic (test gap).
- **Minimum Threshold:** Require **>= 80% Mutation Score** on L2/L3 critical modules (auth, billing, permissions, financial math).

## 2. Ecosystem Tooling
- **TypeScript / JavaScript:** [Stryker Mutator](https://stryker-mutator.io/) (`npx stryker run`)
- **Python:** [mutmut](https://github.com/boxed/mutmut) (`mutmut run --paths-to-mutate <path>`)
- **Rust:** [cargo-mutants](https://github.com/sourcefrog/cargo-mutants) (`cargo mutants`)
- **Go:** [go-mutesting](https://github.com/zimmski/go-mutesting)

## 3. Audit Protocol (`test-guardian` & `release-gatekeeper`)
1. Target critical domain modules (auth, pricing, billing, token validation).
2. Run scoped mutation analysis:
   ```bash
   mutmut run --paths-to-mutate src/billing.py && mutmut results
   ```
3. Write value assertions to kill every surviving mutant on security or payment boundaries before release approval.
