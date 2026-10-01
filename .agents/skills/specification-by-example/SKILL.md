---
name: specification-by-example
description: Transformação de regras vagas em tabelas de exemplos concretos e executáveis.
---

# Specification by Example (SbE) Skill

Esta skill governa a prática de **Specification by Example** no XP Multi-Agent Kit. Em vez de descrever regras em prosa ambígua, o humano e a IA colaboram para expressar o comportamento esperado como **tabelas de exemplos concretos e parametrizados** que são diretamente convertíveis em test fixtures.

---

## 1. Por que Specification by Example com IA?

O maior risco do pair programming com IA é:

> A IA produz código mais rápido do que consegue entender se o código corresponde ao que você queria.

SbE resolve isso porque:
- **Exemplos são inequívocos:** "Saldo R$100, Saque R$101, Resultado: rejeitado" não admite interpretação.
- **Exemplos são verificáveis por máquina:** Cada linha da tabela vira um caso de teste.
- **Exemplos são compreensíveis pelo humano:** Não exigem conhecimento de código.
- **Exemplos capturam edge cases:** Forçam o humano a pensar nos limites antes da implementação.

---

## 2. Formato Canônico da Tabela SbE

### Regra + Exemplos
```markdown
## Specification by Example

### Regra: [Descrição concisa da regra de negócio]

| Input A | Input B | ... | Resultado Esperado | Motivo |
|---------|---------|-----|--------------------|--------|
| valor_1 | valor_1 | ... | resultado_1        | caso normal |
| valor_2 | valor_2 | ... | resultado_2        | edge case |
| valor_3 | valor_3 | ... | resultado_3        | caso de erro |
```

### Exemplo Real: Validação de Saque
```markdown
### Regra: Um usuário não pode sacar mais dinheiro do que possui.

| Saldo    | Saque    | Resultado  | Motivo           |
|----------|----------|------------|------------------|
| R$100,00 | R$50,00  | ✅ Aprovado | Saldo suficiente |
| R$100,00 | R$100,00 | ✅ Aprovado | Saldo exato      |
| R$100,00 | R$100,01 | ❌ Rejeitado | Saldo insuficiente |
| R$0,00   | R$0,01   | ❌ Rejeitado | Saldo zero       |
| R$100,00 | R$-50,00 | ❌ Rejeitado | Valor negativo   |
| R$100,00 | R$0,00   | ❌ Rejeitado | Valor zero       |
```

### Exemplo Real: Criação de Usuário
```markdown
### Regra: Criação de usuário valida email, senha e unicidade.

| Email           | Senha     | Email existe? | Resultado | Código |
|-----------------|-----------|---------------|-----------|--------|
| user@test.com   | Abc123!@  | Não           | Criado    | 201    |
| user@test.com   | Abc123!@  | Sim           | Rejeitado | 409    |
| invalid-email   | Abc123!@  | —             | Inválido  | 422    |
| user2@test.com  | 123       | Não           | Fraca     | 422    |
| (vazio)         | Abc123!@  | —             | Inválido  | 422    |
| user3@test.com  | (vazio)   | —             | Inválido  | 422    |
```

---

## 3. Transformação SbE → Tests (Regra de Conversão)

Cada linha da tabela SbE DEVE gerar **exatamente um caso de teste parametrizado**.

### Python (pytest parametrize)
```python
import pytest

@pytest.mark.parametrize("saldo, saque, aprovado", [
    (100.00, 50.00,  True),   # Saldo suficiente
    (100.00, 100.00, True),   # Saldo exato
    (100.00, 100.01, False),  # Saldo insuficiente
    (0.00,   0.01,   False),  # Saldo zero
    (100.00, -50.00, False),  # Valor negativo
    (100.00, 0.00,   False),  # Valor zero
])
def test_validacao_saque(saldo, saque, aprovado):
    resultado = validar_saque(saldo, saque)
    assert resultado.aprovado == aprovado
```

### JavaScript (test.each)
```javascript
test.each([
  [100, 50,     true,  'saldo suficiente'],
  [100, 100,    true,  'saldo exato'],
  [100, 100.01, false, 'saldo insuficiente'],
  [0,   0.01,   false, 'saldo zero'],
])('saque: saldo=%d saque=%d → aprovado=%s (%s)',
  (saldo, saque, esperado, _motivo) => {
    expect(validarSaque(saldo, saque)).toBe(esperado);
  }
);
```

---

## 4. Checklist de Qualidade da Tabela SbE

Antes de aprovar uma tabela SbE, o humano (e o `navigator`) devem verificar:

- [ ] **Happy path coberto?** Pelo menos um caso de sucesso padrão.
- [ ] **Limites testados?** Valores exatos no limite (ex: saldo == saque).
- [ ] **Erros testados?** Pelo menos um caso de erro por regra de validação.
- [ ] **Edge cases extremos?** Zero, negativo, vazio, nulo, overflow.
- [ ] **Combinações conflitantes?** Quando duas regras interagem (ex: email válido + senha fraca).
- [ ] **Coluna "Motivo" preenchida?** Cada linha deve explicar por que existe.

---

## 5. Integração no Fluxo ATDD

A Specification by Example é a **ponte entre Acceptance Criteria e testes automatizados**:

```text
Acceptance Criteria (abstrato)
    ↓
Specification by Example (concreto)
    ↓
Parameterized Tests (executável)
    ↓
Implementação (código)
```

### Quando usar SbE
- **Obrigatório (L2/L3):** Regras de negócio com múltiplas condições, validações e edge cases.
- **Recomendado (L1):** Quando a regra tem mais de 2 cenários possíveis.
- **Dispensado (L0):** Alterações triviais sem lógica de negócio.

---

## 6. Anti-Padrões

- ❌ **Tabela com 1 linha:** Se só existe um cenário, SbE não agrega valor — use um teste direto.
- ❌ **Tabela sem edge cases:** Se todos os exemplos são happy path, a tabela está incompleta.
- ❌ **Exemplos redundantes:** Linhas que testam exatamente a mesma condição são ruído.
- ❌ **Colunas ambíguas:** "Status" pode significar HTTP code, estado de domínio, ou flag booleano — seja explícito.
- ❌ **Tabela gerada sem revisão humana:** A IA pode propor, mas o humano DEVE revisar e completar os edge cases.
