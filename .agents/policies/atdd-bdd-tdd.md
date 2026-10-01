# ATDD/BDD + TDD: Pirâmide de Especificação & Governança de Contrato

> **Princípio:** O humano define *o que* deve acontecer (contrato comportamental). A IA implementa *como* (código e testes unitários). O Conformance Report prova que um conecta com o outro.

---

## 1. Pirâmide de Especificação (Ordem Obrigatória)

A execução segue estritamente a ordem top-down. É **proibido** iniciar a implementação sem que as camadas superiores estejam definidas e aprovadas:

1. **Acceptance Criteria (ATDD):** Humano define os critérios verificáveis de aceite.
2. **Cenários Gherkin (BDD):** Humano e/ou Navigator formulam cenários `Given / When / Then`.
3. **Specification by Example (SbE):** Humano e/ou Navigator criam tabelas parametrizadas com exemplos concretos (obrigatório para regras com múltiplas condições).
4. **Acceptance Tests (RED):** IA (`test-guardian`) converte cenários e tabelas SbE em testes automatizados que falham.
5. **Integration Tests (RED):** IA decompõe em testes de fronteira (banco, API, filas).
6. **Unit Tests (RED):** IA decompõe em testes unitários de lógica pura.
7. **Implementação (GREEN):** IA (`builder`) codifica apenas o necessário para satisfazer todos os testes.
8. **Refactor:** IA refatora mantendo todos os testes GREEN.
9. **Conformance Report:** IA produz relatório de cobertura de critérios.

---

## 2. Separação de Responsabilidades (Contrato Humano-IA)

| Responsabilidade | Dono | Justificativa |
|---|---|---|
| Intent e requisito de negócio | Humano | Apenas o humano conhece o problema real |
| Acceptance Criteria | Humano | Define "o que significa estar correto" |
| Specification by Example | Humano (IA propõe) | Humano valida edge cases e limites |
| Cenários Gherkin | Humano + IA | Navigator pode formular, humano aprova |
| Acceptance Tests | IA | Conversão mecânica de spec em código |
| Unit / Integration Tests | IA | Decomposição técnica |
| Implementação | IA | Código de produção |
| Conformance Report | IA | Prova de cobertura |
| Review final | Humano | Validação de que o contrato foi cumprido |

### Regra Anti-Self-Test
> É expressamente proibido que a IA defina os Acceptance Criteria E os testes correspondentes sem aprovação humana intermediária. Isso elimina o risco de "100% GREEN mas produto errado".

---

## 3. Ativação por Nível de Risco

| Nível | Acceptance Criteria | SbE Tables | Gherkin | Stop Gate | Conformance Report |
|---|---|---|---|---|---|
| **L0 (Trivial)** | Dispensado | Dispensado | Dispensado | Dispensado | Dispensado |
| **L1 (Small)** | Bullet points informais | Opcional | Opcional | Opcional | Resumido |
| **L2 (Feature)** | **Obrigatório** | **Obrigatório** | **Obrigatório** | **Obrigatório** | **Obrigatório** |
| **L3 (Critical)** | **Obrigatório** | **Obrigatório** | **Obrigatório** | **Obrigatório** | **Obrigatório** + Threat Model |

---

## 4. Regra de Bloqueio (Hard Gate)

- Uma entrega L2/L3 NÃO pode ser declarada DONE se:
  - Algum Acceptance Criteria não possui teste correspondente.
  - Algum teste de aceitação está RED.
  - O Conformance Report não foi gerado (manualmente ou via `agy-conformance --spec <SPEC.md> --tests <dir>`).
  - O humano não aprovou a especificação no Stop Gate.

---

## 5. Relação com Políticas Existentes

Esta política **complementa** e **não substitui** as políticas existentes:

- **`tdd.md`:** Continua governando o ciclo RED→GREEN→REFACTOR na camada de implementação. ATDD adiciona a camada de aceitação *acima* do TDD.
- **`evidence.md`:** O Conformance Report é uma evidência adicional obrigatória. Os níveis L0-L4 de evidência continuam válidos.
- **`agent-handoff.md`:** O Handoff Packet deve incluir o status do Conformance Report e referência à SPEC aprovada.
