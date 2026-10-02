# SPEC-001: Integração Ponytail — Escada de Simplificação, Platform-Native e CLI agy-debt

> **Status:** APPROVED  
> **Risco:** L2 (Expansão de Arquitetura, Políticas, Skills e Ferramental CLI)  
> **Autor:** Antigravity (Pair Programming AI)  
> **Data:** 2026-10-01  

---

## 1. Contexto & Problema de Negócio

- **Por que estamos construindo isso?**  
  Modelos de IA possuem um viés sistemático de *over-engineering*: geram abstrações prematuras (fábricas para classes únicas, wrappers desnecessários), adicionam bibliotecas externas pesadas para utilidades que a plataforma ou a standard library já oferecem nativamente, e produzem explicações mais longas do que o código necessário. A análise do [Ponytail](file:///home/andrevmp/Downloads/xp-multiagent-kit/ponytail-main) comprovou que a aplicação de uma "Escada de 7 Degraus de Simplificação" e de um catálogo de substituição nativa reduz em média 54% das linhas de código, 22% dos tokens e 20% do custo, com 100% de conformidade com segurança.
  
- **Impacto esperado:**  
  1. Redução permanente no footprint de código gerado pelo `builder`;
  2. Eliminação de dependências redundantes via catálogo nativo `platform-native.md`;
  3. Revisões de diff cirúrgicas com gramática de 1 linha no `diff-simplifier-review` e `refactor-warden`;
  4. Rastreamento formal de simplificações e atalhos deliberados via marcadores in-code auditados pelo novo CLI `agy-debt`, com alerta de risco de apodrecimento (*rot risk / no-trigger*).

- **Restrições não negociáveis:**  
  1. **TDD estrito e Anti-Test-Bypass inegociáveis:** A simplificação do código nunca deve justificar redução ou relaxamento da suíte de testes (TDD RED-GREEN-REFACTOR obrigatório em L1-L3; nada de trocar testes por meros `assert demo()`);
  2. **SSDLC & Zero Trust mantidos:** STRIDE e validações de borda não podem ser atalhos;
  3. **Preservação dos 276 testes existentes:** Zero regressão na suíte de testes do kit.

---

## 2. Acceptance Criteria (ATDD)

### AC-1: Catálogo de Soluções Nativas da Plataforma (`platform-native.md`)
- **Dado:** Um desenvolvedor ou agente consultando alternativas a bibliotecas externas.
- **Quando:** O arquivo `.agents/policies/platform-native.md` for acessado.
- **Então:** Deve conter tabelas categorizadas para HTML5, CSS3, Browser/Web APIs, Node.js stdlib e Python stdlib, detalhando as alternativas nativas que substituem bibliotecas populares (date picker, modal, deep clone, debounce, query string, UUID, etc.).
- **Métrica:** Arquivo criado e estruturado com 5 seções tecnológicas e tabela "Você acha que precisa vs O que a plataforma já tem".

### AC-2: Escada de 7 Degraus & Concisão de Output no Builder e Políticas
- **Dado:** O agente `builder` (`.agents/agents/builder/agent.md`), a política `token-economy.md` e `frontend.md`.
- **Quando:** O agente planeja ou implementa código de produção.
- **Então:** Deve obrigatoriamente aplicar a Escada de 7 Degraus (YAGNI → Reuso no Repo → Stdlib → Platform-Native → Deps Existentes → One-Liner → Código Mínimo) e a regra de "Explicação menor que o código" (máx 3 linhas para código executável: o que foi pulado e quando adicionar).
- **Métrica:** Presença da escada e regras em `builder/agent.md`, `token-economy.md` e `frontend.md`.

### AC-3: Gramática Cirúrgica de Over-Engineering no Diff Simplifier e Refactor Warden
- **Dado:** As skills `diff-simplifier-review` (`.agents/skills/diff-simplifier-review/SKILL.md`) e `code-deslop-review` (`.agents/skills/code-deslop-review/SKILL.md`).
- **Quando:** Uma revisão de diff for executada pelo `refactor-warden`.
- **Então:** O formato de apontamento deve seguir a gramática de 1 linha: `L<linha>: <tag> <o que cortar>. <o que substitui>.` onde tag é `delete:`, `stdlib:`, `native:`, `yagni:`, `shrink:`, finalizando com o saldo `net: -N lines, -M deps possible` (ou `Lean already. Ship.`).
- **Métrica:** Formato e tags integrados nas skills e na definição do agente `refactor-warden`.

### AC-4: Convenção de Marcador de Débito Técnico com Teto e Gatilho
- **Dado:** Um atalho ou simplificação deliberada introduzida no código.
- **Quando:** O desenvolvedor insere um comentário de débito.
- **Então:** O formato padrão auditável deve ser `// debt: <teto da simplificação>, <gatilho para refatorar>` (ou `# debt: ...` / `/* debt: ... */` / `<!-- debt: ... -->`), onde o teto define o limite conhecido e o gatilho define a métrica/evento para refatoração.
- **Métrica:** Padrão documentado formalmente na política de memória e qualidade.

### AC-5: Motor CLI `agy-debt` com Detecção de Rot `[NO-TRIGGER]`
- **Dado:** O módulo `scripts/debt_tracker.py` e o executável CLI `agy-debt`.
- **Quando:** Executado no workspace com argumentos `--scan`, `--json`, `--export`, ou `--fail-on-no-trigger`.
- **Então:**
  1. Varre recursivamente arquivos ignorando diretórios de build/sistema (`.git`, `node_modules`, `venv`, `.gemini`, `brain`, `dist`, etc.);
  2. Extrai arquivo, linha, escopo da simplificação, teto (*ceiling*) e gatilho de upgrade (*upgrade trigger*);
  3. Sinaliza `[NO-TRIGGER]` se não houver gatilho de upgrade especificado;
  4. Exibe sumário total de débitos encontrados e contagem de itens em risco de apodrecimento (`no-trigger`);
  5. Retorna código de saída `0` em scan normal, e código `1` se `--fail-on-no-trigger` for fornecido e existirem débitos sem gatilho;
  6. Suporta `--sync-memory` para sincronizar os débitos diretamente na Seção 7 do `PROJECT_MEMORY.md`.
- **Métrica:** Suíte de testes unitários em `tests/test_debt_tracker.py` com 100% de aprovação e cobertura completa de cenários.

### AC-6: Instalação Global & Sincronização do Ecossistema
- **Dado:** O script de instalação `./scripts/install-global.sh`.
- **Quando:** Executado no ambiente.
- **Então:** Cria link simbólico global de `agy-debt` em `~/.local/bin/agy-debt`, sincroniza skills e políticas em `~/.gemini/config/` e atualiza `SKILLS_INDEX.md`.
- **Métrica:** `agy-debt` executável globalmente no terminal e verificado via `agy-health`.

---

## 3. Specification by Example (SbE)

### Regra 1: Extração e Classificação de Marcadores de Débito (`debt_tracker.py`)

| Linha de Código Exemplo | Marcador Detectado | Teto (*Ceiling*) | Gatilho (*Trigger*) | Status Trigger |
|---|---|---|---|---|
| `# debt: scan linear O(N), migrar para B-Tree se tabela > 50k` | Sim | `scan linear O(N)` | `migrar para B-Tree se tabela > 50k` | `OK` |
| `// debt: global lock, per-account locks se RPS > 500` | Sim | `global lock` | `per-account locks se RPS > 500` | `OK` |
| `/* debt: mock simples sem retry */` | Sim | `mock simples sem retry` | `None` | `NO-TRIGGER` |
| `<!-- debt: layout fixo 320px, adicionar flexbox quando suporte a tablet for solicitado -->` | Sim | `layout fixo 320px` | `adicionar flexbox quando suporte a tablet for solicitado` | `OK` |
| `// normal comment: nada a ver` | Não | — | — | Ignorado |

### Regra 2: Códigos de Retorno do CLI `agy-debt`

| Argumentos CLI | Débitos Encontrados | Débitos Sem Gatilho | Exit Code | Saída Chave |
|---|---|---|---|---|
| `--scan` | 3 | 1 | 0 | Tabela formatada + alerta de 1 rot risk |
| `--scan --fail-on-no-trigger` | 3 | 1 | 1 | Mensagem de erro bloqueando CI |
| `--scan --fail-on-no-trigger` | 2 | 0 | 0 | Sucesso limpo |
| `--json` | 2 | 0 | 0 | JSON com array de débitos e sumário |
| `--scan` | 0 | 0 | 0 | `Nenhum débito técnico encontrado. Ledger limpo.` |

---

## 4. Cenários de Aceite (Gherkin BDD)

```gherkin
Feature: CLI agy-debt e Auditoria de Débitos Técnicos

  Scenario: Varredura com detecção de débito e gatilho de upgrade
    Given um repositório com código contendo "# debt: cache em memória, redis se > 1k usuários"
    When eu executo "agy-debt --scan"
    Then a saída deve conter o arquivo e a linha correspondente
    And o teto deve ser "cache em memória"
    And o gatilho deve ser "redis se > 1k usuários"
    And o status deve ser "OK"

  Scenario: Detecção de risco de apodrecimento (no-trigger)
    Given um repositório com código contendo "// debt: atalho temporário"
    When eu executo "agy-debt --scan"
    Then o débito deve ser sinalizado com "[NO-TRIGGER]"
    And a contagem de riscos de apodrecimento deve ser incrementada

  Scenario: Bloqueio de CI para débitos sem gatilho de upgrade
    Given um repositório com 1 débito marcado sem gatilho
    When eu executo "agy-debt --scan --fail-on-no-trigger"
    Then o código de saída deve ser 1
    And a mensagem de erro deve indicar que débitos sem gatilho violam a política
```

---

## 5. Contrato de Domínio & Interfaces

### Schema do Objeto `DebtItem` (`scripts/debt_tracker.py`)
```python
@dataclass
class DebtItem:
    file_path: str
    line_number: int
    raw_comment: str
    ceiling: str
    trigger: Optional[str]
    has_trigger: bool
```

### Assinatura do CLI `agy-debt`
```bash
agy-debt [--scan] [--dir PATH] [--json] [--export PATH] [--fail-on-no-trigger] [--sync-memory]
```

---

## 6. Invariantes & Propriedades

1. **Invariante de Não-Regressão de Testes:** A suíte existente de 276 testes deve continuar com 276/276 aprovados.
2. **Invariante Anti-Test-Bypass:** Nenhum código do `debt_tracker` ou alteração no kit pode ser entregue sem teste unitário prévio correspondente.
3. **Invariante de Não-Poluição de Diretórios:** O scanner do `debt_tracker` nunca deve varrer diretórios de VCS (`.git`), bibliotecas de terceiros (`node_modules`, `venv`, `.venv`), nem arquivos de cache (`__pycache__`, `.pytest_cache`).

---

## 7. Conformance Tracking

| # | Acceptance Criteria | Test File / Verificação | Evidência / Test Name | Status |
|---|---|---|---|---|
| AC-1 | Catálogo Platform-Native | `.agents/policies/platform-native.md` | Inspeção de 5 seções técnicas | ✅ COMPLIANT |
| AC-2 | Escada de 7 Degraus no Builder | `.agents/agents/builder/agent.md`, `token-economy.md` | Presença de Escada de 7 Degraus e regra de concisão | ✅ COMPLIANT |
| AC-3 | Gramática Cirúrgica no Diff Simplifier | `.agents/skills/diff-simplifier-review/SKILL.md` | Formato `L<num>: <tag>` com tags e saldo net | ✅ COMPLIANT |
| AC-4 | Convenção Marcador de Débito | `.agents/policies/token-economy.md` | Padrão `// debt: <teto>, <gatilho>` formalizado | ✅ COMPLIANT |
| AC-5 | Motor CLI `agy-debt` & Detecção de Rot | `tests/test_debt_tracker.py` | 12 testes unitários aprovados (parsing, scan, rot risk) | ✅ COMPLIANT |
| AC-6 | Instalação Global & Links | `scripts/install-global.sh`, `scripts/agy_health.py` | Link `~/.local/bin/agy-debt` ativo (17/17 tools OK) | ✅ COMPLIANT |

**Resultado: 6/6 critérios cobertos (100% COMPLIANT).**

---

## 8. Notas de Implementação

- **Decisões técnicas tomadas:**
  1. A Escada de Simplificação (The Ladder) foi integrada tanto no `builder` quanto no `token-economy.md` e `frontend.md` para garantir enforcement em todas as camadas.
  2. Criado o catálogo `platform-native.md` com soluções prontas para HTML5, CSS3, Web APIs, Node.js e Python standard libraries.
  3. `agy-debt` implementado em Python com regex multilíngue (suportando `#`, `//`, `/* ... */`, `<!-- ... -->`), detecção de gatilho ausente (`[NO-TRIGGER]`), gate de CI (`--fail-on-no-trigger`) e sincronização opcional com `PROJECT_MEMORY.md`.
  4. Suíte de testes expandida de 276 para 288 testes, mantendo 100% de aprovação e zero regressão.

