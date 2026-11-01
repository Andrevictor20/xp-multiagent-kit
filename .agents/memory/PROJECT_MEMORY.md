# Project Memory — XP Multi-Agent Kit v4

## 1. FATOS
- **Stack:** Python 3.10+, stdlib (`unittest`, `sqlite3` FTS5, `pathlib`, `json`, `urllib`), Git, POSIX shell.
- **Comandos Principais:**
  - Testes: `python3 -m unittest discover tests`
  - Lint do Kit: `python3 scripts/kit_lint.py`
  - Gate: `python3 scripts/xp_gate.py check`
  - CLI Unificada: `python3 scripts/xp <subcmd>`
- **Caminhos Críticos:** `scripts/xp`, `.agents/policy.yaml`, `.agents/components.yaml`, `.agents/policies/`, `.agents/runtime/`.

## 2. DECISÕES
- **SQLite FTS5 para agy-context:** Zero dependências externas e latência p95 ~12ms.
- **Thin Harness v4 (SPEC-006):** Contexto base ≤ 8 KB transferindo governança em prosa para código (`xp contract`, `xp gate`, `policy.yaml`).
- **Consolidação de Políticas (12 → 7):** Fusão em 7 políticas modulares; limites numéricos em `kit_constants.py`.
- **EGM (9 → 2 Personas):** `spec_reviewer` e `code_reviewer` com Pass 3 Conformance determinístico.
- **Limpeza de Duplicações:** Remoção de `REPO_MAP.md` e `COMPLETENESS_OVER_SPEED` (fonte única).
- **Skills Catalog JIT (P1):** A métrica de 29.378 B decorre da estimativa min(len, 1200) em `skill_index.py`; no v4 as skills operam sob demanda (JIT) e não no contexto base (fixo ≤ 8 KB).

## 3. PROGRESSO

- **2026-11-01** [Fase 3 SPEC-006]: smart_tool_optimizer (778→170L) e context_compactor (538→133L) divididos; workflow.yaml movido para .agents/graph/; goldfish-spec-review e deploy-pipeline-conductor removidos (25→24 skills); sections/ em todas as 24 skills; kit_lint 100% verde.
- **2026-11-01** [`5363c08`]: Fase 7 — eval benchmark, integridade geral (417 testes PASS).
- **2026-11-01** [`0fccb72`]: Fase 6 — auto-melhoria (xp evolve) e ablação.

## 4. LIÇÕES & REGRAS 'NEVER'
- `never` usar mocks cegos, asserções vazias ou pular (`.skip`) testes (Anti-Test-Bypass).
- `never` criar God Files (> 500 linhas) em scripts ou testes.
- `never` invocar subagentes ou revisão cega por LLM no refatoramento Thin Harness (Regra 0.1).
- `never` adicionar dependências fora da biblioteca padrão Python (Platform-Native).
- `never` alterar `policy.yaml`, `AGENTS.md` ou `.agents/policies/` sem `xp approve`.
- `never` deixar placeholders (`TODO`, `TBD`, `{{...}}`) em planos ou especificações.
