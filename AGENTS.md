# XP Multi-Agent Kit v4 (Thin Harness)

> **Idioma:** Todas as respostas, planos e explicações ao usuário DEVEM ser em Português (PT-BR).

## 1. CONTRATO
Separar O QUÊ (spec, ACs, SbE) do COMO (código, testes). Validar via `xp contract validate`.

## 2. CONTEXTO
Contexto base fixo ≤ 8 KB. Consultar memória/regras JIT via `xp context <query>` e políticas via `xp policy show <id>` (`.agents/policies/INDEX.md`).
**Step 0:** Ler `.agents/memory/PROJECT_MEMORY.md` (incluindo Dead-Ends) antes de propor ou alterar código.

## 3. FERRAMENTAS
Priorizar CLI local `xp` e busca textual (`grep`/`ripgrep`) para impacto; agrupar chamadas independentes no mesmo turno.

## 4. ESTADO
Estado transiente em `.agents/runtime/` (`run.json`, `events.jsonl`, `flow_state.json`), fora do Git.

## 5. POLÍTICA
Governança declarativa em `.agents/policy.yaml` (`auto` | `review` | `human`). Ações destrutivas e arquivos protegidos exigem `xp approve`.

## 6. VERIFICAÇÃO
Rodar `xp gate check` antes de concluir. EGM 3 passes (Spec, Código, `xp conformance`). TDD estrito (RED → GREEN → REFACTOR), 100% rastreabilidade de ACs e Anti-Test-Bypass.
**Zero Correção Cosmética:** Nunca declarar correção sem rodar teste nativo (`exit_code: 0`); todo bug exige teste de regressão.

## 7. RECUPERAÇÃO
Auto-cura determinística na causa raiz. Circuit breaker na 2ª falha idêntica; registrar falhas em Dead-Ends.

## 8. OBSERVABILIDADE
Eventos estruturados via `kit_events.py` em `.agents/runtime/events.jsonl` + recibo operacional.

## Invariantes
- **Stop Gate Humano:** L2/L3 e specs exigem confirmação explícita.
- **Orçamentos:** Limites em `workflow.yaml` / `kit_constants.py`. Atualizar `PROJECT_MEMORY.md` ao fim de cada entrega.
- **Gate Passo 4 (mecânico):** Sem God Files (>500 linhas), `TODO`/`TBD`/`FIXME`, contornos (`as any`, `@ts-ignore`, `# type: ignore`, `# noqa`), skips (`@unittest.skip`, `.skipTest`, `pytest.mark.skip`) ou segredos hardcoded.
