---
name: property-based-testing
description: Property-Based Testing (PBT), invariant verification, and structured fuzzing.
---

# Property-Based Testing (PBT)

Use controlled random input generators and automatic shrinking to uncover edge-case bugs and minimal counterexamples that fixed example tests miss.

## 1. Universal Invariants to Test
1. **Idempotence:** `f(f(x)) == f(x)` (sanitizers, normalizers, deduplication).
2. **Round-Trip:** `deserialize(serialize(x)) == x` (parsers, codecs, DTOs).
3. **Commutativity / Associativity:** Processing order does not alter aggregate totals.
4. **Metamorphic Relations:** Predictable output transformations when inputs scale or permute.

## 2. Recommended Libraries
- **Python:** [Hypothesis](https://hypothesis.readthedocs.io/)
- **TypeScript / JavaScript:** [fast-check](https://github.com/dubzzz/fast-check)
- **Rust:** [proptest](https://github.com/proptest-rs/proptest) / `quickcheck`
- **Go:** `testing/quick` / [rapid](https://github.com/flyingmutant/rapid)

## 3. Canonical Hypothesis Example

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sorting_preserves_length_and_elements(lst):
    sorted_lst = custom_sort(lst)
    assert len(sorted_lst) == len(lst)
    assert sorted(sorted_lst) == sorted_lst
    assert set(sorted_lst) == set(lst)
```

## 4. Mandatory `test-guardian` Targets
Apply Property-Based Testing whenever implementing:
- Parsers, serializers, encoders, and decoders.
- Financial math (interest, fees, discounts, fractional rounding/allocation).
- RBAC/ABAC permission evaluation engines.
