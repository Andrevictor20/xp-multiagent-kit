---
name: conformance-tracker
description: Rastreamento de cobertura de Acceptance Criteria e geração de Conformance Report.
---

# Conformance Tracker Skill

Esta skill governa o **rastreamento de conformidade** entre Acceptance Criteria (definidos pelo humano) e testes automatizados (implementados pela IA), garantindo que o contrato comportamental da especificação foi integralmente cumprido.

---

## 1. Propósito

O Conformance Tracker resolve o problema central do AI-assisted development:

> **100% dos testes passando ≠ produto correto.**

Ele garante que cada Acceptance Criteria da spec possui um teste correspondente e que esse teste está GREEN.

---

## 2. Conformance Report: Formato Canônico

```markdown
## Conformance Report — SPEC-NNN: [Título]

### Resumo
- **Critérios totais:** N
- **Cobertos por testes:** N/N
- **Aprovados (GREEN):** N/N
- **Status:** ✅ COMPLIANT | ❌ NON-COMPLIANT

### Matriz de Rastreabilidade

| # | Acceptance Criteria | SbE Lines | Test File | Test Name | Status |
|---|---|---|---|---|---|
| AC-1 | [descrição] | 3 exemplos | `tests/test_x.py` | `test_ac1_valid` | ✅ GREEN |
| AC-2 | [descrição] | 4 exemplos | `tests/test_x.py` | `test_ac2_duplicate` | ✅ GREEN |
| AC-3 | [descrição] | 2 exemplos | `tests/test_y.py` | `test_ac3_event` | ✅ GREEN |

### Evidência de Execução
- **Comando:** `python3 -m unittest tests/test_x.py tests/test_y.py`
- **Exit code:** 0
- **Output:** [trecho relevante do output real]
```

---

## 3. Regras de Conformidade

### Hard Gates (Bloqueiam a entrega)
1. **Cobertura 100%:** Todo Acceptance Criteria DEVE ter pelo menos um teste correspondente. Critérios sem teste = NON-COMPLIANT.
2. **Todos GREEN:** Cada teste vinculado a um critério DEVE estar passando. Qualquer RED = NON-COMPLIANT.
3. **Evidência real:** O status GREEN deve ser comprovado por execução nativa real (evidence level ≥ L1). Afirmação verbal é rejeitada.

### Soft Gates (Alertas, não bloqueiam)
1. **Cobertura SbE:** Se um critério tem tabela SbE associada, verificar se todos os exemplos da tabela foram convertidos em casos de teste parametrizados.
2. **Testes órfãos:** Testes que não estão vinculados a nenhum Acceptance Criteria devem ser revisados — podem indicar over-testing ou critérios não documentados.

---

## 4. Integração no Ciclo de Entrega

```text
Acceptance Criteria (aprovados)
    ↓
Testes escritos (RED)
    ↓
Implementação (GREEN)
    ↓
Conformance Tracker verifica:
  ├─ Cada AC tem teste? ✅/❌
  ├─ Cada teste está GREEN? ✅/❌
  └─ Evidência é real? ✅/❌
    ↓
Conformance Report gerado
    ↓
Se COMPLIANT → prossegue para review/release
Se NON-COMPLIANT → BLOQUEADO
```

---

## 5. Ativação por Nível de Risco

| Nível | Conformance Report |
|---|---|
| **L0 (Trivial)** | Dispensado |
| **L1 (Small)** | Resumo informal em 1-2 linhas |
| **L2 (Feature)** | **Obrigatório** — formato canônico completo |
| **L3 (Critical)** | **Obrigatório** — formato canônico + cross-reference com Threat Model |

---

## 6. Localização do Report

- **Inline:** Incluído na seção 7 (Conformance Tracking) do template `SPEC-NNN-ATDD.md`.
- **Handoff:** Referenciado no campo `verification_evidence` do Handoff Packet.
- **Memória:** Resumo persistido na entrada correspondente do `PROJECT_MEMORY.md`.

---

## 7. Geração Automática via CLI

O Conformance Report pode ser gerado por script em vez de escrito em prosa pelo modelo:

```bash
agy-conformance --spec docs/specs/SPEC-042.md --tests tests/
```

O script (`scripts/conformance_report.py`) indexa os testes, casa cada AC com testes que mencionam seu identificador e emite exit 1 se o resultado for `NON-COMPLIANT`.
