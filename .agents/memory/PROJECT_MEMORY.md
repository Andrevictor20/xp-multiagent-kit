# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-10-02 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v2.41.0 (Skill Suite Expansion: Software Evolution, Strategic Technical Roadmapping & Capacity Planning, 77 skills)

---

## 1. Quick Project Summary (Semantic)

- **Propósito:** Kit modular de governança, agentes, skills, workflows e políticas para pair programming com IA (XP, Task Routing L0-L3, Pirâmide de Especificação ATDD/BDD, TDD estrito, Anti-Test-Bypass, SSDLC, Engenharia de Causa Raiz, Otimização de Tokens, Memória Contínua em 4 Tiers e Escada de Simplificação Ponytail).
- **Tech Stack:** Antigravity Agent Framework (Markdown + YAML Frontmatter), Python, Bash, Git, GitHub Actions CLI (`gh`). Agnóstico de linguagem de produção.
- **Arquitetura Chave:** Estrutura modular em `.agents/` (11 agentes, 77 skills, 10 workflows, 11 policies, 2 templates e memória viva em 4 tiers). Suíte global em `~/.local/bin/` e espelhamento em `~/.gemini/config/`.
- **Comandos Essenciais:** (Catálogo completo em [details/commands.md](details/commands.md))
  - Instalação Única / Gestão do Kit: `./install.sh` / `agy-kit [doctor|init|sync]`
  - Instalação / Re-sincronização Global: `./scripts/install-global.sh`
  - Diagnóstico Global de Saúde: `agy-health` / `agy-kit doctor`
  - Auditoria de Débitos Técnicos & Simplificações: `agy-debt --scan`
  - Rotação Automática de Memória: `agy-memory-archive`
  - Telemetria de Tokens (Ao Vivo / Acumulada): `agy-tokens --turn` / `agy-tokens --badge`
  - CI/CD Auto-Healer: `agy-ci-heal --status` / `agy-ci-heal --watch --heal --auto-push`

---

## 2. Current Health & System Status

- **Agent Suite Status:** OPERATIONAL (11 Agentes, 77 Skills, 10 Workflows, 11 Policies, 2 Templates, CI/CD Auto-Healer, Rastreador de Débito `agy-debt`, Utilitário CLI `agy-kit` / `xp-kit`, Suíte Global de Tokens e Health Scanner em `~/.local/bin/`).
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (Pirâmide ATDD/BDD com Stop Gate, TDD Multi-Camadas, Anti-Test-Bypass, SSDLC, Root-Cause Debugging, No Workarounds, Code Deslop, 4-Tier Memory e Telemetria de Tokens).
- **Última Execução / Evidência:** `EV-SKILL-EXPANSION-20261002-02` (Skill software-evolution-and-roadmapping criada, sincronizada em 56 projetos e aprovada com 20/20 testes de perfis e índice)
- **Ambiente Ativo:** Local & Global / Antigravity IDE & CLI.
- **⚠️ Alerta de Cota (Pre-Flight Gate):** Operar em Modo Cirúrgico Atômico (`agy-fast` / effort low) sob alta utilização de cota.

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)

| 2026-10-02 | `FEAT` | Planejamento a Longo Prazo & Roadmapping Estratégico (v2.41.0): skill software-evolution-and-roadmapping (horizontes Now/Next/Later, padrão Strangler Fig para modernização de legados, capacity planning, FinOps e governança de EOL/Sunset de APIs RFC 8594), integração em skill_profiles.py (33 skills no backend) e regeneração do SKILLS_INDEX.md | `.agents/skills/*`, `scripts/skill_profiles.py`, `scripts/prune_skills.py` | `PASS (EV-SKILL-EXPANSION-20261002-02)` |
| 2026-10-02 | `FEAT` | Modernização da Suíte de Skills (v2.40.0): fusão canônica de `observability-instrumentation` em `observability-and-slo-engineering`, criação das skills `async-messaging-and-resilience`, `caching-architecture` e `backend-performance-testing`, catálogo de presets em `visual-direction-studio`, sincronização de `skill_profiles.py` e regeneração de `SKILLS_INDEX.md` | `.agents/skills/*`, `scripts/skill_profiles.py`, `scripts/prune_skills.py` | `PASS (EV-SKILL-MODERNIZATION-20261002-01)` |
| 2026-10-02 | `FEAT` | Instalador Unificado & Portabilidade do Kit (v2.39.0): script único install.sh (suporte a one-liner curl e execução local), motor kit_installer.py com DependencyChecker, GlobalInstaller e ProjectInstaller (modo symlinks aprovado no Stop Gate), utilitário CLI agy-kit / xp-kit com doctor/init/sync, documentação no README.md, SPEC-002 aprovada com 6/6 ACs COMPLIANT e 303/303 testes aprovados | `install.sh`, `scripts/kit_installer.py`, `scripts/agy-kit`, `README.md`, `tests/test_kit_installer.py` | `PASS (EV-UNIFIED-INSTALLER-20261002-01)` |
| 2026-10-02 | `FEAT` | Integração Ponytail & Rastreador agy-debt (v2.38.0): Incorporação da Escada de 7 Degraus de Simplificação, política platform-native.md, gramática cirúrgica de 1 linha no diff-simplifier-review e refactor-warden, motor CLI agy-debt com detecção de rot [NO-TRIGGER] e gate de CI, SPEC-001 aprovada com 6/6 ACs COMPLIANT e 288/288 testes aprovados | `.agents/policies/*`, `scripts/debt_tracker.py`, `tests/test_debt_tracker.py` | `PASS (EV-PONYTAIL-INTEGRATION-20261002-01)` |
| 2026-10-01 | `FEAT` | Consumo Híbrido Ponderado & Eliminação de Tetos Artificiais (v2.37.3): linha de consumo híbrida com tokens absolutos, impacto na janela de contexto (% da janela) e distribuição percentual por categoria (Entrada, Ferramentas, Resposta), eliminação de tetos fictícios na cota da Google exibindo métricas oficiais exatas, correção ponderada do RTK e 276/276 testes aprovados | `scripts/token_tracker.py`, `tests/*` | `PASS (EV-HYBRID-CONSUMPTION-PERCENTAGE-20261001-01)` |
| 2026-10-01 | `FEAT` | Integração Nativa RTK v0.49.0 (v2.37.0): delegação semântica em smart_tool_optimizer para comandos elegíveis git/cargo/pytest/gh, invariante never_worse, agregação e exibição de ganhos do RTK no rodapé canônico (agy-tokens --turn) e 275/275 testes aprovados | `scripts/hooks/*`, `scripts/token_tracker.py`, `scripts/output_noise.py`, `tests/*` | `PASS (EV-RTK-INTEGRATION-COMPLETE-20261001-01)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)

- [x] **[DONE] Instalador Unificado & Portabilidade do Kit (v2.39.0): script único install.sh (one-liner curl e local), motor kit_installer.py, injeção de projeto isolado via symlinks, utilitário CLI agy-kit doctor/init/sync, documentação no README.md, SPEC-002 aprovada com 6/6 ACs COMPLIANT e 303/303 testes aprovados.**
- [x] **[DONE] Integração Ponytail & Rastreador agy-debt (v2.38.0): Escada de 7 Degraus de Simplificação no builder/token-economy/frontend, catálogo platform-native.md, gramática cirúrgica de 1 linha de over-engineering, CLI agy-debt com detecção de rot [NO-TRIGGER] e 288/288 testes unitários aprovados.**
- [x] **[DONE] Integração Nativa RTK v0.49.0 (v2.37.0): reescrita semântica de comandos via RTK em `smart_tool_optimizer.py`, invariante `never_worse` em `output_noise.py`, telemetria de tokens economizados no rodapé canônico (`agy-tokens --turn`), compilação/instalação em `install-global.sh` e 275/275 testes aprovados.**

- [x] **[DONE] Governança Mecânica Anti-Tool-Spamming (v2.36.0): Hooks renderizados incondicionalmente no IDE/CLI, interceptação e bloqueio de polling em `manage_task status`, no-reread pós-edição em `smart_tool_optimizer`, Turno 1 batching no `AGENTS.md` e 268/268 testes unitários aprovados.**
- [x] **[DONE] Expansão ATDD/BDD (v2.35.0): Pirâmide de Especificação com separação de contrato humano-IA, skills `acceptance-test-driven` / `specification-by-example` / `conformance-tracker`, policy `atdd-bdd-tdd.md`, template `SPEC-NNN-ATDD.md`, integração nos workflows L1/L2/L3 e 74/74 skills sincronizadas.**
- [x] **[DONE] Suíte Global de Redução de Tokens: agy-sanitize, agy-handoff, agy-audit, agy-skills-profile (perfis de skills), universal.geminiignore e telemetria em 3 camadas.**
- [x] **[DONE] CI/CD Auto-Healer: monitoramento autônomo de GitHub Actions (gh run), extração cirúrgica de logs de erro e loop de autocorreção em até 3 tentativas (L-003).**
*(Entregas anteriores concluídas arquivadas em [archive/HISTORY.md](archive/HISTORY.md))*
- [ ] **[P1] Validar a execução da matriz multi-testes em um projeto piloto complexo.**
- [ ] **[P2] Validar a Pirâmide de Especificação ponta-a-ponta em uma feature L2 real: emitir `SPEC-NNN-ATDD.md`, obter aprovação no Stop Gate, gerar acceptance tests parametrizados e produzir o primeiro Conformance Report `COMPLIANT` de referência.**
- [ ] **[P3] Rotacionar as 2 entregas mais antigas da seção 3 para `archive/HISTORY.md` via `agy-memory-archive` (Memory Lint / sliding window).**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)

> Conteúdo movido para [details/5-architectural-decisions-domain-models-semantic-memory.md](details/5-architectural-decisions-domain-models-semantic-memory.md) (leitura sob demanda).

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)

> Conteúdo movido para [details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md](details/6-gotchas-hurdles-learned-playbooks-procedural-memory.md) (leitura sob demanda).

## 7. Technical Debts & Known Blockers

- **Nenhum bloqueio ativo.** CI/CD Auto-Healer operacional, 276/276 testes unitários aprovados, RTK v0.49.0 ativo em `~/.local/bin/rtk`, comandos integrados em `~/.local/bin/`, git hooks ativos e persistência de disco rigorosamente cumprida.
