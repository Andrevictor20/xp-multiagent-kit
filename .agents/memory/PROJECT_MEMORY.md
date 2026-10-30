# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-10-30 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v3.8.0 (Integração EGM: Protocolo Goldfish Spec Review & Anti-Glazing)

---

## 1. Quick Project Summary (Semantic)

- **Propósito:** Kit modular e agnóstico de governança, agentes, skills, workflows e políticas para pair programming com IA em **Antigravity, OpenCode, Cursor, Codex e Qoder (IDE & CLI)**, orquestrando Task Routing L0-L3, Pirâmide ATDD/BDD, TDD estrito, Anti-Test-Bypass, SSDLC, Motor Multiagente Dinâmico (Boss-Worker), Autocorreção Reflexiva, Otimização de Contexto e Memória Contínua em 4 Tiers.
- **Tech Stack:** Multi-Host Agent Framework (`AGENTS.md`, `opencode.json`, `.cursor/rules/*.mdc`, `.codex/rules/`, `.qoder/rules/`), Python 3.8+, Bash, PowerShell 5.1+, Windows CMD, Git, GitHub Actions CLI (`gh`). Agnóstico de SO (Linux, macOS, Windows).
- **Arquitetura Chave:** `.agents/` (11 agentes, 79 skills `< 4KB` em Inglês, 11 workflows, 12 policies, 2 templates em Token-Dense English com regra mandatória de saída em Português ao usuário; memória viva em 4 tiers). Suíte modular em `scripts/host_adapters.py`, `scripts/mcp_installers.py`, `scripts/spec_tool.py`, `scripts/update_manager.py`, `scripts/windows_support.py`, `scripts/goldfish_review.py` e binários globais `xp-*` / `agy-*` em `~/.local/bin/` (Unix) ou `%USERPROFILE%\.local\bin\` (Windows `.cmd` shims).
- **Comandos Essenciais:** (Catálogo completo em [details/commands.md](details/commands.md))
  - Instalação Linux/macOS: `./install.sh [--global|--project <dir>|--both <dir>] [--target all|...] [--lang pt|en]`
  - Instalação Windows (PowerShell/CMD): `powershell -ExecutionPolicy Bypass -File .\install.ps1` ou `install.cmd`
  - Gestão e Auto-Update do Kit: `xp-kit [doctor|init <dir>|sync|update|version]` / `agy-kit`
  - Ferramenta ATDD de Specs: `xp-spec [new <slug>|validate <file>]` / `agy-spec`
  - Validador Goldfish / Heilmeier: `python3 scripts/goldfish_review.py <doc.md>`
  - Auditoria de Orçamento & Índice de Skills: `python3 scripts/skill_index.py [generate|audit]`
  - Conformidade ATDD & Débitos: `xp-conformance` / `agy-debt --scan`

---

## 2. Current Health & System Status

- **Agent Suite Status:** OPERATIONAL (11 Agentes, 79 Skills `< 4KB` em Inglês, 11 Workflows, 12 Policies, 5 Hosts Nativos com Motor Multiagente Boss-Worker Completo, Toolchain RTK/OD/CRG/Alethe, Auto-Update).
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (373/373 testes unitários e de integração `PASS`, 0 caminhos pessoais, arquivos `< 500` linhas, `PROJECT_MEMORY.md` `< 8KB`).
- **Última Execução / Evidência:** `EV-KIT-V3.8.0-EGM-GOLDFISH-INTEGRATION-20261030` (Integração do modelo Elephant-Goldfish Model: nova skill goldfish-spec-review, 9 personas de revisores cegos, padrões Heilmeier, script utilitário scripts/goldfish_review.py, testes TDD unitários 373/373 PASS e limpeza completa de pastas temporárias e do repositório EGM externo).
- **Ambiente Ativo:** Local & Global / Linux, macOS e Windows nativo (PowerShell / CMD).

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5 Entregas)

| 2026-10-30 | `FEAT` | Integração do Modelo Elephant-Goldfish (EGM) (v3.8.0) — (1) Criação da skill `.agents/skills/goldfish-spec-review/` com as 5 fases de revisão cega, mandatos anti-glazing e 9 personas de críticos hostis em `personas/`, (2) Adição dos padrões de especificação em `resources/` (Heilmeier, Feature Spec, Implementation Readiness), (3) Criação do script de conformidade `scripts/goldfish_review.py`, (4) 4 novos testes unitários TDD em `tests/test_goldfish_review.py` e 373/373 testes totais `PASS`, (5) Limpeza da sandbox de teste e remoção do repositório clonado `elephant-goldfish-model-main/` | `.agents/skills/goldfish-spec-review/`, `scripts/goldfish_review.py`, `tests/test_goldfish_review.py` | `PASS (373/373 tests)` |

| 2026-10-30 | `FEAT` | Expansão Multiagente Multi-Host — Etapas 4 (Cursor) e 5 (Qoder) (v3.7.0) — (1) Implementação de `CursorWorkerDriver` e `QoderWorkerDriver` em `scripts/multiagent_drivers.py`, (2) Provisionamento de `.cursor/rules/30-multiagent-boss-worker.mdc` e exportação dos 11 agentes em `.qoder/agents/*.md`, (3) Respeito estrito à regra No-God-Files (<500 linhas em todos os scripts), (4) 17 novos testes unitários TDD e 369/369 testes PASS | `scripts/multiagent_drivers.py`, `scripts/host_adapters.py`, `tests/test_cursor_multiagent.py`, `tests/test_qoder_multiagent.py` | `PASS (369/369 tests)` |

| 2026-10-30 | `FEAT` | Integração de Toolchain Alethe Orchestrator (v3.6.5) — (1) Implementação da classe `AletheInstaller` em `scripts/mcp_installers.py` no padrão RTK/OpenDesign instalando em `~/.local/share/alethe-orchestrate` e expondo binários `alethe`, `xp-alethe` e `agy-alethe` em `~/.local/bin/`, (2) Integração em `GlobalInstaller` e `essential_bins` de `scripts/kit_installer.py`, (3) Novo teste de interface em `tests/test_spec_003_enhancements.py` com 352/352 testes PASS, (4) Limpeza do diretório staging temporário | `scripts/mcp_installers.py`, `scripts/kit_installer.py`, `tests/test_spec_003_enhancements.py`, `~/.local/` | `PASS (352/352 tests)` |

| 2026-10-30 | `FEAT` | Mandato Rígido de AST CodeReviewGraph (CRG) & Auto-Bootstrap (v3.6.4) — (1) Eliminação do escape hatch 'or grep' em `AGENTS.md`, `.agents/agents/builder/agent.md` e `.agents/policies/token-economy.md`, tornando mandatório o uso de `code-review-graph` (`call_mcp_tool` / `agy-graph`) para Impact Mapping (L1+) e busca de chamadores/testes, (2) Inclusão de `codebase-cartography` no perfil base `CORE_SKILLS` de `scripts/skill_profiles.py` e na persona do `builder`, (3) Auto-bootstrap de `graph.db` no hook `crg-auto-update.sh` em repositórios Git, (4) Injeção de diretiva CRG no dispatcher global `~/.gemini/config/AGENTS.md` e no hook `dynamic_effort_hook.py`, (5) 351/351 testes PASS | `AGENTS.md`, `.agents/`, `scripts/skill_profiles.py`, `scripts/hooks/`, `scripts/host_adapters.py` | `PASS (351/351 tests)` |

| 2026-10-25 | `FEAT/FIX` | Sincronização Universal de Settings, Correção de Variantes Flash e Blindagem de Diretivas (v3.6.3) — (1) Expansão de `sync_global_settings` para sincronizar atomicamente todos os 4 arquivos de settings (`~/.gemini/antigravity-cli/`, `~/.gemini/antigravity-ide/`, `~/.gemini/settings.json`, `~/.gemini/config/`), (2) Eliminação do aviso `--effort is not supported` no CLI 1.4+ passando o ID da variante do modelo (`gemini-3.8-flash-low`), (3) Blindagem contra falsos positivos em `DIRECTIVE_MEDIUM_PATTERNS` / `DIRECTIVE_HIGH_PATTERNS` para relatos narrativos e perguntas sobre comportamento de modo, (4) Baseline neutro de inicialização estabilizado em `low` e perfil `core` de skills, (5) 351/351 testes PASS | `scripts/agy_effort_router.py`, `~/.gemini/` | `PASS (351/351 tests)` |

| 2026-10-24 | `FEAT/FIX` | Turn-1 Fast Multi-Agent Dispatch & Relatório de Agentes (v3.6.1) — (1) Eliminação da pausa intermediária (Stop Gate de planejamento) quando múltiplos agentes são solicitados no prompt inicial; pré-autorização e disparo imediato no Turno 1 via `invoke_subagent`, (2) Implementação da reportagem obrigatória de alocação de agentes no início e Relatório de Execução Multiagente no encerramento (`format_agents_roster` e `format_agents_summary`), (3) Atualização do 4-Point Pre-Response Self-Audit, `AGENTS.md`, `orchestrator/agent.md`, políticas (`atdd-bdd-tdd`, `agent-handoff`), `task-routing`, `host_adapters.py` e sincronização global em `~/.gemini/config/AGENTS.md`, (4) 2 novos testes TDD e 351/351 testes `PASS` | `AGENTS.md`, `.agents/`, `scripts/antigravity_multiagent.py`, `scripts/host_adapters.py`, `tests/test_antigravity_multiagent.py`, `~/.gemini/config/` | `PASS (351/351 tests)` |

| 2026-10-23 | `FEAT` | Expansão Multiagente Multi-Host — Etapa 3: OpenAI Codex CLI & IDE (v3.6.0) — Provisionamento de `.codex/rules/default.rules` (regras Starlark `prefix_rule` autoaprovando suítes de teste no sandbox Bubblewrap) e `.codex/config.toml` (MCPs e modelo padrão), implementação do driver `CodexWorkerDriver` (`codex exec -m ... -c model_reasoning_effort=... --sandbox workspace-write --approve-for-me --worktree --ephemeral`), sincronização global em `~/.codex/` e 7 novos testes unitários TDD | `scripts/host_adapters.py`, `scripts/multiagent_drivers.py`, `tests/test_codex_multiagent.py`, `~/.codex/` | `PASS (349/349 tests)` |

| 2026-10-23 | `FEAT` | Expansão Multiagente Multi-Host — Etapa 2: Claude Code & Desktop (v3.5.0) — Inclusão do Claude em `SUPPORTED_TARGETS`, provisionamento de `CLAUDE.md`, `.mcp.json` e 11 subagentes em `.claude/agents/*.md`, implementação do driver `ClaudeWorkerDriver` (`claude -p --model ... --effort ... --permission-mode bypassPermissions --worktree worker-<id> --output-format json`), sincronização global em `~/.claude/` e 8 novos testes unitários TDD | `scripts/host_adapters.py`, `scripts/multiagent_drivers.py`, `tests/test_claude_multiagent.py`, `~/.claude/` | `PASS (342/342 tests)` |

| 2026-10-23 | `FEAT` | Expansão Multiagente Multi-Host — Etapa 1: OpenCode (v3.4.0) — Enriquecimento de `opencode.json` com schema canônico `agents` (11 agentes especialistas mapeados com `mode: "subagent"`, `default_agent: "orchestrator"`, `subagent_depth: 2`), criação do driver modular `scripts/multiagent_drivers.py` com `OpenCodeWorkerDriver` (`opencode run --agent ... --auto --format json`), suporte a `--host opencode` no CLI `xp-orchestrate` e sincronização global em `~/.config/opencode` | `scripts/host_adapters.py`, `scripts/multiagent_drivers.py`, `scripts/antigravity_multiagent.py`, `tests/test_opencode_multiagent.py`, `~/.config/opencode/` | `PASS (334/334 tests)` |

| 2026-10-23 | `FEAT` | Motor Multiagente Dinâmico Nativo Antigravity (SPEC-004) — Padrão Boss-Worker heterogêneo (Orquestrador em Argon High + Workers paralelos em Flash Low/Med via `invoke_subagent` com `Workspace="branch"`), manifesto estruturado (`.agents/active-mission.json`), memória efêmera (`.agents/MEMORY.md`), dashboard visual ASCII, auto-healing com escalada em 2 fases, relatório final em `mission-report.md`, CLI `agy-orchestrate` e `xp-orchestrate` | `scripts/antigravity_multiagent.py`, `tests/test_antigravity_multiagent.py`, `.agents/templates/`, `.agents/agents/orchestrator/agent.md`, `scripts/windows_support.py`, `scripts/install-global.sh` | `PASS (325/325 tests)` |

| 2026-10-19 | `FEAT` | Remoção Completa da Telemetria de Consumo de Modelos (AGENTS.md, Hooks, CLI & Módulos) — (1) Remoção da obrigatoriedade do rodapé canônico de 4 linhas nas mensagens dos agentes, (2) Exclusão do hook `token-badge` e injeção de rodapé no `dynamic_effort_hook`, (3) Remoção da skill `token-budget-tracker` e regras associadas (`token-telemetry-footer.md`), (4) Remoção de `xp-tokens`/`agy-tokens`, `scripts/token_tracker.py` e `scripts/telemetry/`, (5) Sincronização multi-host limpa (Antigravity, Cursor, Codex, Qoder, OpenCode) e 287/287 testes `PASS` | `AGENTS.md`, `.agents/`, `scripts/`, `tests/` | `PASS (287/287 tests)` |

| 2026-10-18 | `FIX` | Auditoria & Blindagem Multi-Host da Telemetria (Antigravity, Cursor, Codex, Qoder, OpenCode) — (1) Sincronização do template canônico de 4 linhas em todas as regras globais dos 5 hosts (`~/.cursor/rules/00-xp-core.mdc`, `~/.qoder/rules/xp-governance.md`, `~/.codex/rules/xp-governance.md`, `~/.codex/instructions.md`, `~/.config/opencode/AGENTS.md`), (2) Correção do exemplo obsoleto no `README.md`, (3) Execução e aprovação de 100% da suíte de testes (350/350 tests `PASS`) | `AGENTS.md`, `README.md`, `scripts/host_adapters.py`, `~/.cursor/`, `~/.qoder/`, `~/.codex/`, `~/.config/opencode/` | `PASS (350/350 tests)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

### 📌 Ponto de Parada Atual (Sessão 2026-10-30):
- **Status:** Concluídas com sucesso as **Etapas 4 (Cursor Multi-Agent)** e **5 (Qoder Multi-Agent)** via trabalho colaborativo multiagente (`test-guardian` e `builder`).
- **Suíte de Testes:** 369/369 testes PASS (100% GREEN, zero regressão, 17 novos testes unitários adicionados).
- **Cobertura Multi-Host:** Antigravity, OpenCode, Claude Code, OpenAI Codex, Cursor e Qoder 100% suportados no padrão Boss-Worker em worktrees git isoladas.

### 📋 O que Falta para a Próxima Sessão:
1. **[P1] Projeto Piloto Multi-IDE:**
   - Validar execução ponta a ponta de um projeto real integrando os múltiplos hosts simultaneamente em repositório externo.
2. **[P2] Enriquecimento de Playbooks no Motor Nativo:**
   - Inspirar-se nos playbooks do Alethe (`scout-then-build` e `advisor-escalation`) para criar templates adicionais no `xp-orchestrate`.

### Backlog Geral:
- [x] **[DONE] Etapa 1: OpenCode Multi-Agent Engine (Schema `agents`, `subagent_depth: 2`, `OpenCodeWorkerDriver`, `--host opencode`).**
- [x] **[DONE] Etapa 2: Claude Multi-Agent Engine (Claude Code CLI headless `claude -p`, `CLAUDE.md`, `.claude/agents/*.md`, `.mcp.json`, `ClaudeWorkerDriver`).**
- [x] **[DONE] Etapa 3: Codex Multi-Agent Engine (Codex CLI headless `codex exec`, `.codex/rules/default.rules`, `config.toml`, `CodexWorkerDriver`).**
- [x] **[DONE] Etapa 4: Cursor Multi-Agent Engine (`.cursor/rules/30-multiagent-boss-worker.mdc`, `CursorWorkerDriver`).**
- [x] **[DONE] Etapa 5: Qoder Multi-Agent Engine (`.qoder/rules/30-multiagent-boss-worker.md`, `.qoder/agents/*.md`, `QoderWorkerDriver`).**
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
