# Project Memory — XP Multi-Agent Kit v4

## 1. FATOS
- **Stack:** Python 3.10+, stdlib exclusivo (`unittest`, `sqlite3` FTS5, `pathlib`, `json`, `urllib`), Git, POSIX shell.
- **Comandos Principais:**
  - Testes: `python3 -m unittest discover tests`
  - Lint do Kit: `python3 scripts/kit_lint.py`
  - Gate de Execução: `python3 scripts/xp_gate.py check`
  - CLI Unificada: `python3 scripts/xp <subcommand>`
- **Caminhos Críticos:** `scripts/xp`, `.agents/policy.yaml`, `.agents/components.yaml`, `.agents/policies/`, `.agents/runtime/`.

## 2. DECISÕES
- **SQLite FTS5 para agy-context:** Zero dependências externas e latência p95 ~12ms para busca local indexada.
- **Thin Harness v4 (SPEC-006):** Redução do contexto base fixo de ~23.5 KB para ≤ 8 KB transferindo governança em prosa para verificações de software determinísticas (`xp contract`, `xp gate`, `policy.yaml`).
- **Consolidação de Políticas (12 → 7):** Fusão de regras fragmentadas em 7 arquivos temáticos modulares carregados JIT sob demanda; constantes numéricas unificadas em `kit_constants.py`.
- **EGM 2 Personas:** Redução de 9 para 2 personas especializadas (`spec_reviewer` e `code_reviewer`) com Pass 3 Conformance determinístico, cortando custo de tokens.
- **Remoção de REPO_MAP.md e COMPLETENESS_OVER_SPEED:** Eliminação de mapa estático defasado e constante redundante para prevenir alucinações e conflitos de fonte única.

## 3. PROGRESSO
- **2026-11-01** [`3019eb1`]: Conclusão da Fase 0 — baseline e SPEC-006 Thin Harness.
- **2026-11-01** [`e00b965`]: Conclusão da Fase 1 — contrato, política, gate, eventos e recibo (AC-1 a AC-4).
- **2026-11-01** [`7e64671`]: Conclusão da Fase 2 — cortes seguros, contexto ≤ 8KB, políticas consolidadas (7 arquivos) e fonte única.
- **2026-11-01** [`c41adb9`]: Conclusão da Fase 3 — grafo mínimo, workflow.yaml, xp flow e congelamento RED.
- **2026-11-01** [`2155853`]: Conclusão da Fase 4 — 6 agentes nucleares, 2 personas EGM, packs e gancho <=400B.
- **2026-11-01** [fase 5]: EGM em 3 passes, gatilho de >8 arquivos, hook PreInvocation <=400B e fusão de compressores.

## 4. LIÇÕES & REGRAS 'NEVER'
- `never` usar mocks cegos, asserções vazias, ou pular (`.skip`) testes para mascarar falhas (Anti-Test-Bypass rígido).
- `never` criar God Files (> 500 linhas) em scripts ou suítes de teste.
- `never` invocar subagentes ou revisão cega por LLM durante o refatoramento do Thin Harness (Regra 0.1).
- `never` adicionar dependências de runtime fora da biblioteca padrão Python (Platform-Native First).
- `never` alterar `policy.yaml`, `AGENTS.md` ou `.agents/policies/` de forma autônoma sem comando `xp approve`.
- `never` deixar placeholders (`TODO`, `TBD`, `{{...}}`) em planos ou especificações de entrega.
