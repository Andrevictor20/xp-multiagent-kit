# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-10-24 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v3.6.1 (Disparo Multiagente Imediato Turno 1 & Relatório de Agentes)

---

## 1. Quick Project Summary (Semantic)

- **Propósito:** Kit modular e agnóstico de governança, agentes, skills, workflows e políticas para pair programming com IA em **Antigravity, OpenCode, Cursor, Codex e Qoder (IDE & CLI)**, orquestrando Task Routing L0-L3, Pirâmide ATDD/BDD, TDD estrito, Anti-Test-Bypass, SSDLC, Motor Multiagente Dinâmico (Boss-Worker), Autocorreção Reflexiva, Otimização de Contexto e Memória Contínua em 4 Tiers.
- **Tech Stack:** Multi-Host Agent Framework (`AGENTS.md`, `opencode.json`, `.cursor/rules/*.mdc`, `.codex/rules/`, `.qoder/rules/`), Python 3.8+, Bash, PowerShell 5.1+, Windows CMD, Git, GitHub Actions CLI (`gh`). Agnóstico de SO (Linux, macOS, Windows).
- **Arquitetura Chave:** `.agents/` (11 agentes, 78 skills `< 4KB` em Inglês, 11 workflows, 12 policies, 2 templates em Token-Dense English com regra mandatória de saída em Português ao usuário; memória viva em 4 tiers). Suíte modular em `scripts/host_adapters.py`, `scripts/mcp_installers.py`, `scripts/spec_tool.py`, `scripts/update_manager.py`, `scripts/windows_support.py` e binários globais `xp-*` / `agy-*` em `~/.local/bin/` (Unix) ou `%USERPROFILE%\.local\bin\` (Windows `.cmd` shims).
- **Comandos Essenciais:** (Catálogo completo em [details/commands.md](details/commands.md))
  - Instalação Linux/macOS: `./install.sh [--global|--project <dir>|--both <dir>] [--target all|...] [--lang pt|en]`
  - Instalação Windows (PowerShell/CMD): `powershell -ExecutionPolicy Bypass -File .\install.ps1` ou `install.cmd`
  - Gestão e Auto-Update do Kit: `xp-kit [doctor|init <dir>|sync|update|version]` / `agy-kit`
  - Ferramenta ATDD de Specs: `xp-spec [new <slug>|validate <file>]` / `agy-spec`
  - Auditoria de Orçamento & Índice de Skills: `python3 scripts/skill_index.py [generate|audit]`
  - Conformidade ATDD & Débitos: `xp-conformance` / `agy-debt --scan`

---

## 2. Current Health & System Status

- **Agent Suite Status:** OPERATIONAL (11 Agentes, 78 Skills `< 4KB` em Inglês, 11 Workflows, 12 Policies, 5 Hosts, Motor Multiagente Dinâmico Nativo, Toolchain RTK/OD/CRG, Auto-Update).
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (351/351 testes unitários e de integração `PASS`, 0 caminhos pessoais, arquivos `< 500` linhas, `PROJECT_MEMORY.md` `< 8KB`).
- **Última Execução / Evidência:** `EV-KIT-V3.6.1-TURN1-MULTIAGENT-REPORT-20261024-01` (Eliminação de parada artificial intermediária ao solicitar múltiplos agentes no prompt inicial, despacho imediato Turno 1 via invoke_subagent, quadro de alocação inicial de agentes e relatório de execução multiagente mandatório no encerramento, 4-Point Pre-Response Self-Audit e 351/351 testes PASS).
- **Ambiente Ativo:** Local & Global / Linux, macOS e Windows nativo (PowerShell / CMD).

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5 Entregas)

| 2026-10-24 | `FEAT/FIX` | Turn-1 Fast Multi-Agent Dispatch & Relatório de Agentes (v3.6.1) — (1) Eliminação da pausa intermediária (Stop Gate de planejamento) quando múltiplos agentes são solicitados no prompt inicial; pré-autorização e disparo imediato no Turno 1 via `invoke_subagent`, (2) Implementação da reportagem obrigatória de alocação de agentes no início e Relatório de Execução Multiagente no encerramento (`format_agents_roster` e `format_agents_summary`), (3) Atualização do 4-Point Pre-Response Self-Audit, `AGENTS.md`, `orchestrator/agent.md`, políticas (`atdd-bdd-tdd`, `agent-handoff`), `task-routing`, `host_adapters.py` e sincronização global em `~/.gemini/config/AGENTS.md`, (4) 2 novos testes TDD e 351/351 testes `PASS` | `AGENTS.md`, `.agents/`, `scripts/antigravity_multiagent.py`, `scripts/host_adapters.py`, `tests/test_antigravity_multiagent.py`, `~/.gemini/config/` | `PASS (351/351 tests)` |

| 2026-10-23 | `FEAT` | Expansão Multiagente Multi-Host — Etapa 3: OpenAI Codex CLI & IDE (v3.6.0) — Provisionamento de `.codex/rules/default.rules` (regras Starlark `prefix_rule` autoaprovando suítes de teste no sandbox Bubblewrap) e `.codex/config.toml` (MCPs e modelo padrão), implementação do driver `CodexWorkerDriver` (`codex exec -m ... -c model_reasoning_effort=... --sandbox workspace-write --approve-for-me --worktree --ephemeral`), sincronização global em `~/.codex/` e 7 novos testes unitários TDD | `scripts/host_adapters.py`, `scripts/multiagent_drivers.py`, `tests/test_codex_multiagent.py`, `~/.codex/` | `PASS (349/349 tests)` |

| 2026-10-23 | `FEAT` | Expansão Multiagente Multi-Host — Etapa 2: Claude Code & Desktop (v3.5.0) — Inclusão do Claude em `SUPPORTED_TARGETS`, provisionamento de `CLAUDE.md`, `.mcp.json` e 11 subagentes em `.claude/agents/*.md`, implementação do driver `ClaudeWorkerDriver` (`claude -p --model ... --effort ... --permission-mode bypassPermissions --worktree worker-<id> --output-format json`), sincronização global em `~/.claude/` e 8 novos testes unitários TDD | `scripts/host_adapters.py`, `scripts/multiagent_drivers.py`, `tests/test_claude_multiagent.py`, `~/.claude/` | `PASS (342/342 tests)` |

| 2026-10-23 | `FEAT` | Expansão Multiagente Multi-Host — Etapa 1: OpenCode (v3.4.0) — Enriquecimento de `opencode.json` com schema canônico `agents` (11 agentes especialistas mapeados com `mode: "subagent"`, `default_agent: "orchestrator"`, `subagent_depth: 2`), criação do driver modular `scripts/multiagent_drivers.py` com `OpenCodeWorkerDriver` (`opencode run --agent ... --auto --format json`), suporte a `--host opencode` no CLI `xp-orchestrate` e sincronização global em `~/.config/opencode` | `scripts/host_adapters.py`, `scripts/multiagent_drivers.py`, `scripts/antigravity_multiagent.py`, `tests/test_opencode_multiagent.py`, `~/.config/opencode/` | `PASS (334/334 tests)` |

| 2026-10-23 | `FEAT` | Motor Multiagente Dinâmico Nativo Antigravity (SPEC-004) — Padrão Boss-Worker heterogêneo (Orquestrador em Argon High + Workers paralelos em Flash Low/Med via `invoke_subagent` com `Workspace="branch"`), manifesto estruturado (`.agents/active-mission.json`), memória efêmera (`.agents/MEMORY.md`), dashboard visual ASCII, auto-healing com escalada em 2 fases, relatório final em `mission-report.md`, CLI `agy-orchestrate` e `xp-orchestrate` | `scripts/antigravity_multiagent.py`, `tests/test_antigravity_multiagent.py`, `.agents/templates/`, `.agents/agents/orchestrator/agent.md`, `scripts/windows_support.py`, `scripts/install-global.sh` | `PASS (325/325 tests)` |

| 2026-10-19 | `FEAT` | Remoção Completa da Telemetria de Consumo de Modelos (AGENTS.md, Hooks, CLI & Módulos) — (1) Remoção da obrigatoriedade do rodapé canônico de 4 linhas nas mensagens dos agentes, (2) Exclusão do hook `token-badge` e injeção de rodapé no `dynamic_effort_hook`, (3) Remoção da skill `token-budget-tracker` e regras associadas (`token-telemetry-footer.md`), (4) Remoção de `xp-tokens`/`agy-tokens`, `scripts/token_tracker.py` e `scripts/telemetry/`, (5) Sincronização multi-host limpa (Antigravity, Cursor, Codex, Qoder, OpenCode) e 287/287 testes `PASS` | `AGENTS.md`, `.agents/`, `scripts/`, `tests/` | `PASS (287/287 tests)` |

| 2026-10-18 | `FIX` | Auditoria & Blindagem Multi-Host da Telemetria (Antigravity, Cursor, Codex, Qoder, OpenCode) — (1) Sincronização do template canônico de 4 linhas em todas as regras globais dos 5 hosts (`~/.cursor/rules/00-xp-core.mdc`, `~/.qoder/rules/xp-governance.md`, `~/.codex/rules/xp-governance.md`, `~/.codex/instructions.md`, `~/.config/opencode/AGENTS.md`), (2) Correção do exemplo obsoleto no `README.md`, (3) Execução e aprovação de 100% da suíte de testes (350/350 tests `PASS`) | `AGENTS.md`, `README.md`, `scripts/host_adapters.py`, `~/.cursor/`, `~/.qoder/`, `~/.codex/`, `~/.config/opencode/` | `PASS (350/350 tests)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

### 📌 Ponto de Parada Atual (Sessão 2026-10-23):
- **Status:** Pausado a pedido do usuário após conclusão bem-sucedida da **Etapa 3 (OpenAI Codex)**.
- **Suíte de Testes:** 349/349 testes PASS (100% GREEN, zero regressão).
- **Pesquisa Concluída:** Artefato `multiagent-expansion-research.md` preservado na memória contínua com todas as diretrizes para Cursor e Qoder.

### 📋 O que Falta para a Próxima Sessão:
1. **Etapa 4: Cursor Multi-Agent Engine**
   - Criar `tests/test_cursor_multiagent.py` (TDD RED).
   - Em `scripts/host_adapters.py`: atualizar `install_cursor_project()` para gerar `.cursor/rules/30-multiagent-boss-worker.mdc` (instruindo Cursor Composer / Background Agent sobre delegação e portões TDD). *Atenção rigorosa: manter `host_adapters.py` estritamente < 500 linhas.*
   - Em `scripts/multiagent_drivers.py`: implementar `CursorWorkerDriver(BaseWorkerDriver)` e registrar em `get_worker_driver("cursor")`.
   - Executar testes e sincronizar regras globais em `~/.cursor/rules/`.
2. **Etapa 5: Qoder Multi-Agent Engine**
   - Criar `tests/test_qoder_multiagent.py` (TDD RED).
   - Em `scripts/host_adapters.py`: exportar os 11 agentes especialistas para `.qoder/agents/<name>.md` e regras associadas.
   - Em `scripts/multiagent_drivers.py`: implementar `QoderWorkerDriver(BaseWorkerDriver)` formatando `qoder -p "<prompt>" -m <model> --yolo -o json -w <worktree>`.
   - Executar testes e sincronizar globalmente em `~/.qoder/`.
3. **Verificação Final:**
   - Rodar suíte completa (`python3 -m unittest discover tests`).
   - Auditoria de linhas (`wc -l scripts/*.py` < 500 linhas).

### Backlog Geral:
- [x] **[DONE] Etapa 1: OpenCode Multi-Agent Engine (Schema `agents`, `subagent_depth: 2`, `OpenCodeWorkerDriver`, `--host opencode`).**
- [x] **[DONE] Etapa 2: Claude Multi-Agent Engine (Claude Code CLI headless `claude -p`, `CLAUDE.md`, `.claude/agents/*.md`, `.mcp.json`, `ClaudeWorkerDriver`).**
- [x] **[DONE] Etapa 3: Codex Multi-Agent Engine (Codex CLI headless `codex exec`, `.codex/rules/default.rules`, `config.toml`, `CodexWorkerDriver`).**
- [ ] **[P1] Etapa 4: Cursor Multi-Agent Engine (`.cursor/rules/*.mdc`, composer/worktree background execution, `CursorWorkerDriver`).**
- [ ] **[P2] Etapa 5: Qoder Multi-Agent Engine (`.qoder/rules/*.md`, `.qoder/agents/*.md`, qoder CLI headless, `QoderWorkerDriver`).**
- [x] **[DONE] Instalador nativo para Windows (PowerShell/CMD/Batch) com shims .cmd e configuração de PATH via winreg.**
- [x] **[DONE] Suporte ao Codex CLI e matriz de 5 hosts (Antigravity, OpenCode, Cursor, Codex, Qoder).**
- [x] **[DONE] Toolchain embutida no instalador: RTK (compilação cargo/download), OpenDesign e CodeReviewGraph.**
- [x] **[DONE] Reforço ATDD/BDD com CLI `xp-spec`/`agy-spec` e hook de disciplina ATDD.**
- [x] **[DONE] Eliminação total de caminhos e referências pessoais do desenvolvedor em arquivos rastreados.**
- [x] **[DONE] Catálogo de modelos multi-ferramenta e telemetria adaptativa por host (`--host`).**
- [x] **[DONE] Motor de Auto-Update `xp-kit update` com cache de 24h e notificações discretas.**
- [x] **[DONE] Matriz de instalação flexível: global, projetos específicos (`--project`), ou ambos (`--both`).**
- [x] **[DONE] Documentação técnica completa em inglês no `README.md`.**
- [x] **[DONE] Ferramenta de empacotamento comercial e validação Agensi.io (`xp-pack` / `agy-pack`) com TDD e pacotes iniciais.**
- [ ] **[P1] Validar execução de projeto piloto multi-IDE (OpenCode + Cursor + Codex + Qoder) em repositório externo.**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)

> Conteúdo em [details/5-architectural-decisions-domain-models-semantic-memory.md](details/5-architectural-decisions-domain-models-semantic-memory.md) (sob demanda).

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)

> Conteúdo em [details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md](details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md) (sob demanda).

## 7. Technical Debts & Known Blockers

- **Nenhum bloqueio ativo.** Orçamento de contexto base (`AGENTS.md`, `PROJECT_MEMORY.md`, 77 `SKILL.md` e `SKILLS_INDEX.md`) 100% dentro dos tetos de `kit_constants.py`.


- 2026-10-23 `DOC/ANALYSIS` (L0): Adicionado `Especificacao Tecnica...` ao `.gitignore` e conduzida análise arquitetural de viabilidade do motor multiagente dinâmico heterogêneo (Boss-Worker) para o kit.
- 2026-10-22 `FEAT` (L1): Ponytail v5 parcial — Impact Map no `builder`; tags `risk/perf/test/gap` e audit repo-wide em `diff-simplifier-review`/`refactor-warden`. Band/Board descartados.
