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

## 3. PROGRESSO
- **2026-11-01** [`3019eb1`]: Fase 0 — baseline e SPEC-006 Thin Harness.
- **2026-11-01** [`e00b965`]: Fase 1 — contrato, política, gate, eventos e recibo (AC-1 a AC-4).
- **2026-11-01** [`7e64671`]: Fase 2 — cortes seguros, contexto ≤ 8KB, 7 políticas e fonte única.
- **2026-11-01** [`c41adb9`]: Fase 3 — workflow.yaml, xp flow e congelamento RED.
- **2026-11-01** [`2155853`]: Fase 4 — 6 agentes nucleares, 2 personas EGM e packs.
- **2026-11-01** [`f7c92da`]: Fase 5 — EGM 3 passes, gatilho >8 arquivos, hook <=400B.
- **2026-11-01** [`0fccb72`]: Fase 6 — auto-melhoria (xp evolve) e ablação.
- **2026-11-01** [`5363c08`]: Fase 7 — eval benchmark, README ≤120L, integridade geral (427 testes PASS).
- **2026-11-01** [`a454c0e`]: Poda de 63 skills redundantes (80 → 25) e arquivos dist/i/docs comerciais; economia de ~59 KB por turno.
- **2026-11-01** [git-hygiene]: Exclusão de planos na raiz, blindagem no .gitignore e documentação Git no README.

## 4. LIÇÕES & REGRAS 'NEVER'
- `never` usar mocks cegos, asserções vazias ou pular (`.skip`) testes (Anti-Test-Bypass).
- `never` criar God Files (> 500 linhas) em scripts ou testes.
- `never` invocar subagentes ou revisão cega por LLM no refatoramento Thin Harness (Regra 0.1).
- `never` adicionar dependências fora da biblioteca padrão Python (Platform-Native).
- `never` alterar `policy.yaml`, `AGENTS.md` ou `.agents/policies/` sem `xp approve`.
- `never` deixar placeholders (`TODO`, `TBD`, `{{...}}`) em planos ou especificações.
