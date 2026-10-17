---
name: specification-by-example
description: Convert ambiguous business rules into executable Specification by Example tables.
---

# Specification by Example (SbE)

Replace ambiguous prose requirements with concrete, parameterized example tables that translate 1:1 into automated test fixtures.

## 1. Canonical SbE Table Format

```markdown
## Specification by Example

### Rule: A user cannot withdraw more than their available balance.

| Balance | Withdrawal | Expected Result | Reason               |
|---------|------------|-----------------|----------------------|
| 100.00  | 50.00      | ✅ Approved     | Sufficient balance   |
| 100.00  | 100.00     | ✅ Approved     | Exact boundary       |
| 100.00  | 100.01     | ❌ Rejected     | Insufficient balance |
| 0.00    | 0.01       | ❌ Rejected     | Zero balance         |
| 100.00  | -50.00     | ❌ Rejected     | Negative amount      |
| 100.00  | 0.00       | ❌ Rejected     | Zero amount          |
```

## 2. Direct 1:1 Conversion to Parameterized Tests
Every row in an SbE table MUST generate a parameterized test case:

### Python (`pytest` / `unittest.subTest`)
```python
import pytest

@pytest.mark.parametrize("balance, withdrawal, approved", [
    (100.00, 50.00,  True),   # Sufficient balance
    (100.00, 100.00, True),   # Exact boundary
    (100.00, 100.01, False),  # Insufficient balance
    (0.00,   0.01,   False),  # Zero balance
    (100.00, -50.00, False),  # Negative amount
    (100.00, 0.00,   False),  # Zero amount
])
def test_withdrawal_validation(balance, withdrawal, approved):
    assert validate_withdrawal(balance, withdrawal).approved is approved
```

### TypeScript / JavaScript (`test.each`)
```typescript
test.each([
  [100, 50,     true,  'sufficient balance'],
  [100, 100,    true,  'exact boundary'],
  [100, 100.01, false, 'insufficient balance'],
  [0,   0.01,   false, 'zero balance'],
])('withdrawal(%d, %d) -> approved=%s (%s)', (balance, amount, expected) => {
  expect(validateWithdrawal(balance, amount)).toBe(expected);
});
```

## 3. SbE Table Quality Checklist
- [ ] **Happy path** covered?
- [ ] **Exact boundary values** tested (`balance == withdrawal`)?
- [ ] **Validation errors** covered (at least 1 row per rejection rule)?
- [ ] **Extreme edge cases** included (`0`, negative, empty, `null`, overflow)?
- [ ] **Conflicting rule combinations** tested (e.g., valid email + weak password)?
- [ ] **Reason column** filled for every row?

## 4. Activation & Anti-Patterns
- **Mandatory (L2/L3):** Multi-condition business rules, pricing/financial calculations, and state machines.
- **Anti-Patterns:** 1-row tables, happy-path-only tables, ambiguous column names, or AI-generated tables shipped without human Stop-Gate review.
