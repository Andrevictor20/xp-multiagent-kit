# Project Memory — XP Multi-Agent Kit v4

## 1. FATOS
- **Stack:** Python 3.10+ stdlib (`unittest`, `sqlite3` FTS5, `pathlib`, `json`), Git, POSIX shell.
- **Comandos:** Testes `python3 -m unittest discover tests` | Lint `python3 scripts/kit_lint.py` | Gate `xp gate check` | CLI `python3 scripts/xp <subcmd>`.
- **Caminhos:** `scripts/xp`, `.agents/policy.yaml`, `.agents/components.yaml`, `.agents/policies/INDEX.md`, `.agents/runtime/`.

## 2. DECISÕES
- **Thin Harness v4 (SPEC-006):** Base fixa ≤ 8 KB; governança em código (`xp contract`, `xp gate`, `policy.yaml`).
- **Políticas JIT (7 arquivos):** Índice compacto em `.agents/policies/INDEX.md`; corpo via `xp policy show <id>` ou `xp context <query>`.
- **SQLite FTS5:** Busca JIT sem deps externas (~12ms p95).
- **EGM (2 Personas):** `spec_reviewer` + `code_reviewer` + Pass 3 `xp conformance`.
- **Design Craft:** 7 skills `craft*` via `designer/agent.md` e `workflow.yaml`.
- **CLI Única `xp`:** Wrappers legados `agy-*`, `contrib/` e scripts sobrepostos removidos; descrições de skills/agentes limitadas a ≤ 110 chars via `kit_lint.py`.

## 3. PROGRESSO
- **2026-11-21 (Benchmark & Token Opt):** Suíte A/B híbrida (`llm_{adapters,tasks,runner,aggregate}.py`) + remoção de `ephemeralMessage` em L0/L1 (KV-cache), hints autossuficientes em `xp_gate`/`xp_contract` e auto-registro TDD em `tool-size-guard`: **−3,6% tokens** (`170.642` vs `177.059`, `T02` de `88.268` para `23.050`), **6/6** resolvidas, **5/5** L1+ com `GATE PASS`.
- **2026-11-21 (ADK Patterns):** Memória multi-repo (`scripts/memory_store.py`: `user:`/`repo:`/`session:`, FTS5 indexando Dead-Ends e `never`, `xp memory promote|consolidate`) + `xp_flow.py` v2 (`output_key` whiteboard, `on_fail: retry|reopen:<nó>` com circuit breaker, nós `parallel:` concorrentes).
- **2026-11-21 (Lean v4):** −69 arquivos mortos (`contrib/`, 12 wrappers `agy-*`, scripts legados, stubs `0-resumo.md`, packs quebrados); 0 `# noqa`/`# type: ignore`; 10 refs em agentes corrigidas; OpenCode `INDEX.md`; custo fixo −30% (−60% OpenCode).

## 4. LIÇÕES & REGRAS 'NEVER'
- `never` usar mocks cegos, asserções vazias ou `.skip` (Anti-Test-Bypass).
- `never` criar God Files (> 500 linhas) ou adicionar deps fora da stdlib Python.
- `never` alterar `policy.yaml`, `AGENTS.md` ou `.agents/policies/` sem aprovação (`xp approve`).
- `never` deixar `TODO`/`TBD`/`FIXME` ou `# noqa`/`# type: ignore` no código do kit.
- `never` afirmar correção sem teste nativo comprovando `exit_code: 0`.

## 5. TENTATIVAS QUE FALHARAM (DEAD-ENDS)
- Nenhum dead-end registrado até o momento no kit v4.
