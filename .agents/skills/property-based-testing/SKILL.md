---
name: property-based-testing
description: Geração automatizada de testes baseados em propriedades e fuzzing estruturado para descobrir casos de borda e invariantes de domínio.
---

# Property-Based Testing Skill

Esta skill governa a aplicação de **Property-Based Testing (PBT)** no XP Multi-Agent Kit, utilizando geradores aleatórios controlados e *shrinking* para encontrar falhas obscuras e contra-exemplos mínimos em algoritmos e regras de negócio complexas.

---

## 1. Por que Testes Baseados em Propriedades?
Testes unitários baseados em exemplos fixos testam apenas os casos em que o desenvolvedor pensou. O Property-Based Testing inverte essa dinâmica: o desenvolvedor define **invariantes universais** que devem sempre ser válidas para qualquer entrada, e a ferramenta gera centenas de casos de teste agressivos automaticamente.

### Invariantes Canônicos:
1. **Idempotência:** `f(f(x)) == f(x)` (ex: sanitização de strings, deduplicação).
2. **Round-trip (Serialização/Deserialização):** `deserialize(serialize(obj)) == obj`.
3. **Comutatividade / Associatividade:** Ordem de processamento não altera o resultado consolidado.
4. **Metamorfismo:** Relações previsíveis entre entradas alteradas e saídas correspondentes.

---

## 2. Bibliotecas Recomendadas
- **Python:** [Hypothesis](https://hypothesis.readthedocs.io/)
- **TypeScript / JavaScript:** [fast-check](https://github.com/dubzzz/fast-check)
- **Rust:** [proptest](https://github.com/proptest-rs/proptest) ou [quickcheck](https://github.com/BurntSushi/quickcheck)
- **Go:** [testing/quick](https://pkg.go.dev/testing/quick) ou [rapid](https://github.com/flyingmutant/rapid)

---

## 3. Exemplo Prático de Invariante com Hypothesis

```python
from hypothesis import given, strategies as st

# Exemplo de invariante: qualquer lista ordenada preserva o tamanho original e os mesmos elementos
@given(st.lists(st.integers()))
def test_sorting_preserves_length_and_elements(lst):
    sorted_lst = custom_sort(lst)
    assert len(sorted_lst) == len(lst)
    assert sorted(sorted_lst) == sorted_lst
    assert set(sorted_lst) == set(lst)
```

---

## 4. Integração com o Test-Guardian
O `test-guardian` aplica Property-Based Testing obrigatoriamente em:
- Parsers, encoders e decoders de dados.
- Algoritmos de cálculo de juros, taxas, descontos e divisões fracionárias.
- Motores de permissão e controle de acesso RBAC/ABAC.
