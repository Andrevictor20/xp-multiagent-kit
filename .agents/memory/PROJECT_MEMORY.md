# 🧠 Project Memory & Context Snapshot

> **Última Atualização:** 2026-09-25 18:18 (Local)  
> **Status Geral do Projeto:** STABLE  
> **Versão / Marco Atual:** v2.23.0 (Docs Sync: Full Alignment of README.md with Quadruple Tool Governance, Effort Router & AST Repo Map)

---

## 1. Quick Project Summary (Semantic)
- **Propósito:** Kit modular de governança, agentes, skills, workflows e políticas para pair programming com IA baseado na metodologia Extreme Programming (XP), Task Routing adaptativo por risco (L0-L3), TDD estrito com Matriz Multi-Camadas, Política Anti-Test-Bypass, SSDLC, Engenharia de Causa Raiz & Anti-Workaround, Code Deslop, DevOps & Zero-Downtime Deployments, Observabilidade & SLOs, Cloud Security & Zero Trust Architecture, Engenharia de Frontend Anti-Slop, Motor de Conversion Copywriting, Suíte Global de Otimização de Tokens no Antigravity (IDE & CLI), CI/CD Auto-Healer com Loop Autônomo de Autocorreção e Sistema de Memória Contínua em 4 Tiers com Auto-Onboarding, Recaptura Retroativa de Histórico Git (Reverse Ingestion), Instalação Global no Antigravity (`~/.gemini/config/`) e Hard-Enforced Disk Persistence Gate.
- **Tech Stack:** Antigravity Agent Framework (Markdown + YAML Frontmatter), Agnóstico de linguagem de produção, Python, Bash, Git, GitHub Actions CLI (`gh`).
- **Arquitetura Chave:** Estrutura modular em `.agents/` contendo `agents` (11 especialistas), `skills` (63 capacidades granulares com `ci-auto-heal`), `workflows` (7 esteiras L0-L3 com Passo 0 e Passo Final autônomos), `policies` (9 regras inegociáveis), `templates` (scaffolds) e `memory` (memória viva em 4 tiers, auto-onboarding, recaptura git e arquivo permanente). Suíte global instalada em `~/.local/bin/` (`agy-ci-heal`, `xp-ci-heal`, `agy-tokens`, `xp-tokens`, `agy-apply-ignore`, `agy-sanitize`, `agy-handoff`, `agy-audit`, `agy-fast`, `agy-deep`). Paridade e espelhamento integral em `~/.gemini/antigravity-cli/` e `~/.gemini/antigravity-ide/`.
- **Comandos Essenciais:**
  - Instalação / Re-sincronização Global: `./scripts/install-global.sh`
  - Telemetria de Tokens por Mensagem (Ao Vivo): `agy-tokens --turn` ou `xp-tokens --turn`
  - Telemetria de Tokens Acumulada: `agy-tokens --badge` ou `agy-tokens --check`
  - Implantação Universal de Ignore: `agy-apply-ignore` ou `python3 scripts/apply_ignore_rules.py`
  - CI/CD Auto-Healer: `agy-ci-heal --status` ou `agy-ci-heal --watch --heal --auto-push`
  - Diagnóstico Cirúrgico de CI: `agy-ci-heal --diagnose-run <run-id>`
  - Sanitizador Anti-Flood: `agy-sanitize <cmd>` ou `<cmd> | agy-sanitize`
  - Handoff / Reset de Sessão: `agy-handoff --write-file`
  - Auditoria de Configuração: `agy-audit`
  - Validação Git: `git status && git log -n 5 --oneline`

---

## 2. Current Health & System Status
- **Agent Suite Status:** OPERATIONAL (11 Agentes, 63 Skills, 7 Workflows, 9 Policies, CI/CD Auto-Healer, Suíte Global de Tokens em `~/.local/bin/`, Configuração Global Ativa em `~/.gemini/config/`, Paridade Total em `~/.gemini/antigravity-ide/`, Memória em 4 Tiers com Persistência Forçada em Disco)
- **Quality Gate / Rules:** 100% compliant com `AGENTS.md` (TDD Multi-Camadas, Anti-Test-Bypass, SSDLC, Zero-Downtime, IaC Governance, Observability RED, CloudSec OIDC, Root-Cause Debugging, No Workarounds, Code Deslop, Frontend Anti-Slop, 4-Tier Memory, Auto-Onboarding, Reverse Ingestion, CI/CD Auto-Healing com limite L-003, Telemetria Obrigatória por Mensagem e Hard Disk Persistence)
- **Última Execução / Evidência:** `EV-DOCS-README-SYNC-20260925-01` (Sincronização integral do README.md e PROJECT_MEMORY.md com as novas ferramentas, hooks, esforço dinâmico e skills)
- **Ambiente Ativo:** Local & Global / Antigravity IDE & CLI

---

## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)

| 2026-09-25 | `DOCS` | Sincronização do README.md com o estado real do repositório: documentação completa dos 63 skills, governança quádrupla de ferramentas (Smart Tool Optimizer, Tool Size Guard, Token Badge, Dynamic Effort Router), roteamento inteligente de reasoning effort (agy-smart, agy-effort, agy-fast, agy-deep), AST Repo Map (REPO_MAP.md), telemetria de tokens em 3 camadas, CI/CD auto-healer e guia de instalação global | `README.md`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-DOCS-README-SYNC-20260925-01)` |
| 2026-09-25 | `FEAT` | Governança Quádrupla de Ferramentas e Otimização Inteligente de Tokens: (1) Loop Detection no hook smart_tool_optimizer.py (bloqueio automático de 3 chamadas repetidas com os mesmos argumentos via hash sha256), (2) Clamp de list_dir na raiz do workspace e injeção automática de filtros de ruído em grep_search, (3) Repo Map Atômico (< 80 linhas / ~1.2k tokens) via scripts/repo_map.py e comando global agy-repo-map, (4) Atualização de AGENTS.md e project-memory skill com Passo 0 e Auto-Compact | `scripts/hooks/smart_tool_optimizer.py`, `scripts/repo_map.py`, `scripts/agy-repo-map`, `scripts/install-global.sh`, `AGENTS.md`, `.agents/skills/project-memory/SKILL.md`, `tests/test_smart_tool_optimizer.py`, `tests/test_repo_map.py` | `PASS (EV-QUADRUPLE-TOOL-GOV-20260925-01)` |
| 2026-09-25 | `FEAT` | Auto-Sanitização Universal no Smart Tool Optimizer (PreToolUse Hook): expansão de cobertura para 100% dos comandos ruidosos e pipelines desprotegidos (test runners, linters, builds, package managers, git inspection, container logs e discovery), suporte a comandos prefixados por variáveis de ambiente, subshell para comandos encadeados (&&, ;, ||), preservação estrita do exit code de comandos falhos via `set -o pipefail` e 6 novos testes unitários dedicados (83/83 testes passando no total) | `scripts/hooks/smart_tool_optimizer.py`, `tests/test_smart_tool_optimizer.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-UNIVERSAL-AUTO-SANITIZE-20260925-01)` |
| 2026-09-25 | `FEAT` | Modulação Automática e Contextual de Reasoning Effort no CLI & IDE: correção do router e hook PreInvocation para analisar o histórico acumulado do transcript (multi-turn), detecção robusta de diretrizes explícitas em linguagem natural ("Mude para o effort high", "coloque em high", "/effort high"), herança automática do risco ativo (L2/L3) em prompts de continuação pós Stop Gate ("continue", "prossiga", "pode fazer"), preservação do modo HIGH configurado no startup interativo do agy, sincronização global em 4 settings.json (CLI, IDE, global e config), desduplicação cross-process via hash MD5 e 5 novos testes unitários (77/77 total) | `scripts/agy_effort_router.py`, `scripts/hooks/dynamic_effort_hook.py`, `tests/test_agy_effort_router.py`, `tests/test_dynamic_effort_hook.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-CONTEXT-DYNAMIC-EFFORT-20260925-01)` |
| 2026-09-25 | `FEAT` | Modulação Dinâmica de Reasoning Effort Turno-a-Turno no CLI (`PreInvocation` Hook): hook `dynamic-effort-hook.py` intercepta cada prompt do usuário via `transcript.jsonl`, reclassifica semanticamente o risco da tarefa (L0-L3), sincroniza `settings.json` (CLI & IDE), exibe badge no terminal e injeta `ephemeralMessage` com diretriz de esforço no modelo antes da resposta; 4 novos testes unitários (72/72 total) | `scripts/hooks/dynamic_effort_hook.py`, `tests/test_dynamic_effort_hook.py`, `.agents/hooks.json`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-DYNAMIC-CLI-EFFORT-20260925-01)` |
| 2026-09-25 | `FEAT` | Smart Tool Optimizer Ativo (PreToolUse Hook com overwrite): interceptação inteligente de ferramentas em runtime para IDE e CLI; clamp automático de view_file para máx 40 linhas, injeção automática de agy-sanitize em run_command verboso sem limitador, hook registrado em .agents/hooks.json com paridade global e suíte de 11 testes unitários dedicados (68/68 no total do projeto) | `scripts/hooks/smart_tool_optimizer.py`, `tests/test_smart_tool_optimizer.py`, `.agents/hooks.json`, `AGENTS.md`, `.agents/skills/token-budget-tracker/SKILL.md`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-SMART-TOOL-OPTIMIZER-20260925-01)` |
| 2026-09-25 | `FEAT` | Detecção Dinâmica e Exibição de Reasoning Effort na Telemetria CLI & IDE: inclusão do nível de esforço ativo (High, Medium, Low, Thinking) nas saídas `agy-tokens` (`--turn`, `--plain`, `--rich`, `--badge`, `--report`, `--json`), parâmetro CLI `-e`/`--effort`, detecção a partir de `USER_SETTINGS_CHANGE`, `settings.json` e env vars, com 54/54 testes aprovados | `scripts/token_tracker.py`, `tests/test_token_tracker.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-CLI-EFFORT-DISPLAY-20260925-01)` |
| 2026-09-25 | `FEAT` | Política de Relatório Exaustivo de Consumo no Chat & Detalhes de Refresh ao Vivo: governança no `AGENTS.md` e skill `token-budget-tracker` obrigando detalhamento máximo (modelo/limites, cotas oficiais ao vivo, refresh times, decomposição e status), inclusão de refresh nas saídas JSON, plain e rich do `token_tracker.py` e 50/50 testes aprovados | `AGENTS.md`, `.agents/skills/token-budget-tracker/SKILL.md`, `scripts/token_tracker.py`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-CHAT-EXHAUSTIVE-TELEMETRY-20260925-01)` |
| 2026-09-25 | `FEAT` | Exibição Explícita de Modelo Utilizado e Limites Dinâmicos na Telemetria CLI: inclusão do nome amigável e raw do modelo ativo com detecção dinâmica e flag `-m`/`--model`, exibição explícita dos limites do modelo (janela de contexto e saída máxima) nos comandos `agy-tokens`/`xp-tokens` (`--plain`, `--rich`, `--turn`, `--badge`, `--report`, `--json`), inspeção adicional de `settings.json` e 25/25 testes unitários aprovados | `scripts/token_tracker.py`, `tests/test_token_tracker.py`, `.agents/skills/token-budget-tracker/SKILL.md`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-CLI-MODEL-LIMITS-20260925-01)` |
| 2026-09-25 | `FEAT` | Router Inteligente de Reasoning Effort no CLI (`agy-smart`, `agy-effort`): classificação semântica L0-L3 (low/medium/high), heurística por git context (branch/arquivos modificados), sincronização atômica de `settings.json` (CLI & IDE), salvaguarda de cota com downshift quando 5h/semanal > 80% e suite com 9 testes unitários dedicados (47/47 total) | `scripts/agy_effort_router.py`, `scripts/agy-effort`, `scripts/global-token-optimizer/agy-wrapper.sh`, `scripts/install-global.sh`, `scripts/global-token-optimizer/install-shell-aliases.sh`, `AGENTS.md`, `tests/test_agy_effort_router.py` | `PASS (EV-CLI-EFFORT-ROUTER-20260925-01)` |
| 2026-09-25 | `FEAT` | Redução Drástica de Consumo de Ferramentas: limite cirúrgico de view_file restrito a 40 linhas, agy-sanitize/pipes obrigatórios para run_command, hook PostToolUse tool-size-guard no hooks.json, alerta de alto uso de tools (>1.5k) no footer e session reset antecipado para 15 turnos / 40k tokens | `AGENTS.md`, `.agents/skills/token-budget-tracker/SKILL.md`, `scripts/hooks/tool-size-guard.py`, `.agents/hooks.json`, `scripts/token_tracker.py`, `tests/test_token_tracker.py` | `PASS (EV-TOOL-REDUCTION-20260925-01)` |
| 2026-09-24 | `FEAT` | Protocolo de Elevação de Esforço Sob Demanda (Gate Medium -> High): IDE mantida em Medium como baseline; ao atingir L2/L3 com plano pronto, o agente emite alerta explícito e pausa a execução aguardando confirmação de troca para High antes de implementar | `AGENTS.md`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-GATE-HIGH-20260924-01)` |
| 2026-09-24 | `FEAT` | Protocolo Zero-Tool para Consultas (L0) & Desativação do Plugin GCP Datacloud: plugin googlecloudtools.datacloud_telemetry desativado (33 skills removidas do overhead global), AGENTS.md reforçado com proibição estrita de invocação de ferramentas para dúvidas conceituais e modulação de concisão | `AGENTS.md`, `~/.gemini/config/plugins_disabled/`, `.agents/memory/PROJECT_MEMORY.md` | `PASS (EV-ZERO-TOOL-20260924-01)` |
| 2026-09-24 | `CHORE` | Desativação Global de Servidores MCP: mcp_config.json zerado (mcpServers: {}), caches de schemas em antigravity-ide/mcp e antigravity-cli/mcp movidos para mcp_disabled; auditoria agy-audit confirmou 0 MCP servers ativos | `~/.gemini/config/mcp_config.json`, `~/.gemini/antigravity-ide/mcp`, `~/.gemini/antigravity-cli/mcp` | `PASS (EV-MCP-DISABLE-20260924-01)` |
| 2026-09-24 | `FEAT` | Telemetria Oficial de Quota ao Vivo via Language Server RPC & Implantação Universal de Ignore: token_tracker.py agora consulta RetrieveUserQuotaSummary em tempo real no daemon local da IDE via ConnectRPC (com fallback resiliente para heurística), corrigindo discrepâncias na janela móvel de 5h e semanal; hook PostInvocation sanitizado; script apply_ignore_rules.py imunizou 54 projetos e agy-apply-ignore adicionado ao PATH | `scripts/token_tracker.py`, `scripts/apply_ignore_rules.py`, `scripts/hooks/token-badge-hook.py`, `scripts/install-global.sh`, `tests/test_token_tracker.py` | `PASS (EV-TOKEN-LIVE-20260924-01)` |
| 2026-09-21 | `FEAT` | Exibição de Telemetria de Tokens Após Cada Mensagem (Delta + 3 Camadas): suporte universal a modelos Google (Gemini 3.8/3.7/3.1/2.5/2.0/1.5) e demais (Claude 4.6/3.7/3.5, GPT-4o, o1, o3-mini, DeepSeek), detecção dinâmica por transcript, comandos agy-tokens/xp-tokens --turn, hook post-invocation token-badge-hook.py e regra mandatória em AGENTS.md | `scripts/token_tracker.py`, `scripts/hooks/token-badge-hook.py`, `.agents/hooks.json`, `AGENTS.md`, `.agents/skills/token-budget-tracker/SKILL.md`, `scripts/install-global.sh`, `tests/test_token_tracker.py` | `PASS (EV-TOKEN-MSG-20260921-01)` |
| 2026-09-21 | `FEAT` | Paridade Global IDE & CLI, Desduplicação de Regras e Acoplamento de Git Hooks: remoção de links redundantes em ~/.gemini/, isolamento de 33 skills legadas GCP em plugin, espelhamento total em ~/.gemini/antigravity-ide/, git hook pre-push/post-push e correção de broken symlink em ~/.bashrc | `scripts/install-global.sh`, `scripts/global-token-optimizer/install-shell-aliases.sh`, `scripts/hooks/post-push-watcher.sh`, `scripts/agy-audit-config`, `tests/test_agy_audit_config.py` | `PASS (EV-GLOBAL-ENFORCE-20260921-02)` |
| 2026-09-21 | `FEAT` | CI/CD Auto-Healer & Loop Autônomo de Autocorreção: ci_healer.py (comandos agy-ci-heal/xp-ci-heal), extração cirúrgica de falhas via gh CLI, salvaguarda de 3 iterações (L-003), skill ci-auto-heal e hook post-push | `scripts/ci_healer.py`, `scripts/hooks/post-push-watcher.sh`, `.agents/skills/ci-auto-heal/SKILL.md`, `AGENTS.md`, `.agents/workflows/release.md`, `tests/test_ci_healer.py` | `PASS (EV-CI-AUTO-HEAL-20260921-01)` |
| 2026-09-21 | `FEAT` | Suíte Global de Redução de Tokens no Antigravity (IDE & CLI em qualquer projeto): agy-sanitize, agy-handoff, agy-audit, perfis de CLI agy-fast/agy-deep, aliases Fish/Bash, universal.geminiignore e guia prático | `scripts/agy-sanitize`, `scripts/agy-handoff`, `scripts/agy-audit-config`, `scripts/global-token-optimizer/*`, `templates/universal.geminiignore`, `docs/universal-token-reduction-guide.md`, `tests/` | `PASS (EV-GLOBAL-TOKEN-OPT-20260921-01)` |
| 2026-09-21 | `FEAT` | Implementação dos 4 Pilares de Redução de Tokens: Protocolo Anti-Flood de Ferramentas, sanitize-tool-output.sh, auditoria de gargalos (--audit), Session Reset aos 25 turnos e modulação de reasoning effort | `scripts/token_tracker.py`, `scripts/sanitize-tool-output.sh`, `AGENTS.md`, `.agents/skills/token-budget-tracker/` | `PASS (EV-TOKEN-OPTIMIZE-20260921-02)` |

---

## 4. Active Backlog & Immediate Handoff (Working / Episodic)
- [x] **[DONE] Exibição de Consumo de Tokens Após Cada Mensagem (IDE & CLI): delta por mensagem (in/tools/out) e acumulado em 3 camadas, suporte multi-modelo com detecção dinâmica e hook PostInvocation (34/34 testes unitários).**
- [x] **[DONE] CI/CD Auto-Healer: monitoramento autônomo de GitHub Actions (gh run), extração cirúrgica de logs de erro, loop de autocorreção em até 3 tentativas (L-003) e hook post-push.**
- [x] **[DONE] Suíte Global de Redução de Tokens (IDE & CLI em qualquer projeto): agy-sanitize, agy-handoff, agy-audit, perfis de CLI (fast/deep) e universal.geminiignore com 28/28 testes unitários aprovados.**
- [x] **[DONE] Otimização de consumo de tokens: orçamento de Rules e Skills < 20% com zero truncamento.**
- [x] **[DONE] Instalação global e linkagem de 63 skills, 9 políticas, 7 workflows e 11 agentes em ~/.gemini/config/.**
- [x] **[DONE] Cross-referencing exaustivo de todos os pacotes e arquivos no AGENTS.md.**
- [x] **[DONE] Hard-Enforcement Gate para escrita física obrigatória em disco no PROJECT_MEMORY.md em todos os workflows e agentes.**
- [x] **[DONE] Token Optimization & Tracker: Telemetria em 3 Camadas (Contexto, 5h e Semanal), binários xp-tokens/agy-tokens, skill token-budget-tracker e eliminação de injeções redundantes.**
- [x] **[DONE] 4 Pilares de Redução de Tokens: Protocolo Anti-Flood de Ferramentas, sanitize-tool-output.sh, auditoria de gargalos (--audit), Session Reset aos 25 turnos e modulação de reasoning effort.**
- [ ] **[P1] Validar a execução da matriz multi-testes em um projeto piloto complexo.**

---

## 5. Architectural Decisions & Domain Models (Semantic Memory)
- **2026-09-21 - CI/CD Auto-Healer & Loop Autônomo de Autocorreção:** Mecanismo autônomo acoplado ao GitHub Actions (`gh` CLI) para monitoramento em tempo real de esteiras, isolamento cirúrgico de logs de falha (`agy-ci-heal`), TDD local corretivo e re-push automático com teto estrito de 3 iterações (Regra [L-003]) para prevenção de loops infinitos.
- **2026-09-21 - Suíte Global de Redução de Tokens no Antigravity:** Desacoplamento da otimização de tokens do escopo exclusivo do kit para abranger qualquer pasta/repositório aberto na máquina via `~/.local/bin/` (`agy-sanitize`, `agy-handoff`, `agy-audit`, `agy-fast`, `agy-deep`) e aliases em `fish`/`bash`, com governança de `.geminiignore` e limites de linha de saída.
- **2026-09-21 - 4 Pilares de Otimização de Tokens:** Combate sistemático ao acúmulo de histórico reenviado através de (1) Protocolo Anti-Flood em comandos e leituras, (2) Desduplicação de rules globais, (3) Rotação compulsória aos 25 turnos / 70k tokens e (4) Modulação de esforço de raciocínio por nível de risco (L0-L3).
- **2026-09-21 - Telemetria de Tokens em 3 Camadas:** O kit diferencia rigorosamente (1) Janela de Mensagem/Sessão (Context Window até 1M/2M tokens), (2) Janela Móvel de 5 Horas (Rolling Rate Limit de curto prazo) e (3) Limite Semanal (Weekly Quota Cycle). Utilitário `xp-tokens` calcula agregação em tempo real através dos bancos SQLite e transcripts do Antigravity.
- **2026-09-05 - Paridade Antigravity CLI e Auto-Aprovação de Edições:** Configuração unificada em `~/.gemini/antigravity-cli/settings.json` com `agentMode: "accept-edits"` e `permissions.allow: ["write_file(*)", "read_file(*)", "command(*)", "mcp(*)", "read_url(*)"]`. Symlinks espelhados em `~/.gemini/antigravity-cli/` garantem que o ecossistema multiagente e a governança XP funcionem identicamente no terminal sem fricção de confirmações repetitivas.
- **2026-08-31 - Otimização de Token Budget no Antigravity:** `rules/` e `plugins/.../rules` não devem conter symlinks redundantes de agents/policies/workflows (que são carregados sob demanda). O `AGENTS.md` atua como regra mestre única e as descrições no frontmatter YAML das skills são mantidas concisas (1-2 frases), reduzindo o consumo de tokens em >75%.
- **2026-08-31 - Instalação Global por Symlinks:** Configuração de `~/.gemini/config/` apontando diretamente para o repositório mestre, permitindo que todas as regras, skills e workflows fiquem ativos globalmente e sejam atualizados em tempo real a cada edição.
- **2026-08-31 - Hard-Enforced Memory Disk Persistence:** Proibição estrita de encerramento de tarefas ou respostas de conclusão sem chamada explícita de ferramenta (`write_to_file`/`replace_file_content`) no `PROJECT_MEMORY.md`.

---

## 6. Gotchas, Hurdles & Learned Playbooks (Procedural Memory)
- **[L-001] Schema Injection em Frontend:** Validar scripts de dados estruturados Schema.org JSON-LD via Browser / Rich Results Test.
- **[L-002] Viewport Shifts no Mobile:** Uso estrito de `min-h-[100dvh]` em vez de `h-screen`.
- **[L-003] Regra dos 3 Fixes em Debugging:** Três falhas consecutivas indicam problema arquitetural.
- **[L-004] Autenticação OIDC em CI/CD:** GitHub Actions requer permissão `id-token: write` no workflow.
- **[L-005] Anti-Test-Bypass Check:** Nunca checar apenas o tipo retornado (`typeof`); valide sempre os valores exatos de negócio (`id`, `status`, `amount`).
- **[L-006] Auto-Onboarding de Repositórios:** Se o repositório aberto for novo ou diferente do kit, o Passo 0-A deve detectar manifestos e reconstruir `PROJECT_MEMORY.md` imediatamente antes de qualquer outra ação.
- **[L-007] Ingestão Reversa de Commits:** Usar formato conciso de git log (`%h - %ad : %s`) com janela deslizante de 5 a 10 commits para não estourar o orçamento de tokens da memória ativa.
- **[L-008] Bash set -e em Incrementos Aritméticos:** No bash com `set -e`, a expressão `(( count++ ))` quando `count=0` avalia para 0 e retorna status de saída 1, abortando o script. Use sempre `count=$((count + 1))` ou `(( count += 1 ))`.
- **[L-009] Token Budget de Customizações no Antigravity:** Arquivos colocados em `rules/` ou descrições verbosas em `SKILL.md` são injetados diretamente em cada turno. Mantenha `rules/` enxuto (apenas regras mestras) e o frontmatter YAML de skills com no máximo 1-2 sentenças objetivas.
- **[L-010] 3 Camadas de Limites no Antigravity:** Não confundir a janela de contexto da mensagem com os limites de rate limit da API. O modelo pode suportar 1M de tokens por turno, mas rajadas contínuas de 50k+ tokens podem atingir a barreira móvel de 5 horas ou o teto semanal da conta.
- **[L-011] Pre-Flight Token Gate & Modo Cirúrgico Atômico:** Sempre alertar o usuário quando qualquer camada estiver crítica (>80% em 5h/Semana ou >70% no Contexto). Se o usuário insistir em rodar, dimensionar o escopo estritamente para o que for cabível no orçamento restante, garantindo um checkpoint completo, testado e estável, proibindo deixar trabalho quebrado ou pela metade.
- **[L-012] O Maior Devorador de Tokens é o Histórico de Ferramentas:** Em sessões longas, saídas volumosas de terminal (logs de testes/builds) e leituras de arquivos inteiros sem StartLine/EndLine representam mais de 50% dos tokens faturados a cada novo turno. Use sempre sanitize-tool-output.sh e grep cirúrgico.
- **[L-013] Sanitização Transparente com Preservação de Exit Code:** O `agy-sanitize` trunca saídas excessivas intermediárias mantendo o topo (head) e a cauda diagnóstica (tail), propagando 100% o código de retorno para garantir compatibilidade com scripts de automação e pipelines de CI.
- **[L-014] Rotação Cirúrgica de Sessão via Handoff Packet:** Usar `agy-handoff --write-file` ao aproximar-se de 25 turnos para gerar um resumo de menos de 25 linhas (~300 tokens). Abrir um novo chat com esse pacote restaura o modelo à velocidade máxima e reduz os custos por turno em mais de 90%.
- **[L-015] Auditoria Proativa de Configuração Global:** O utilitário `agy-audit` monitora a saúde de `~/.gemini/config/`, alertando sobre inchaço de regras (>150 linhas), servidores MCP configurados como `eager` e quantidade excessiva de skills globais (>50) que causam descarte de contexto.
- **[L-016] Extração Cirúrgica de Logs de CI/CD:** Falhas de CI/CD contêm em média 95% de ruído em seus logs brutos (prints de instalação e setup). A filtragem focada em blocos `##[error]`, `Error:`, `FAILED` e stack traces pelo `ci_healer.py` reduz o contexto a menos de 10 linhas, viabilizando o auto-diagnóstico sem estourar a janela de contexto.
- **[L-017] Desduplicação de Regras e Paridade IDE/CLI:** Ter links symlink simultâneos em `~/.gemini/` e `~/.gemini/config/` faz o Antigravity carregar regras globais multiplicadas por 3. Mantenha `AGENTS.md` exclusivamente em `~/.gemini/config/` e garanta que `~/.gemini/antigravity-ide/` espelhe a mesma estrutura de pastas do CLI (`agents`, `workflows`, `skills`, `policies`, `templates`, `rules`).
- **[L-019] Protocolo de Elevação de Esforço Sob Demanda (Gate Medium -> High):** O usuário mantém a IDE fixada em `Medium` como baseline para conversas e planejamento. Quando a tarefa atingir risco L2 (Feature complexa) ou L3 (Arquitetura crítica/Segurança), o agente conclui o plano de implementação, emite um alerta explícito solicitando a alteração para `High` e PAUSA obrigatoriamente a execução. A implementação só é iniciada após o usuário confirmar a alteração do nível de esforço.
- **[L-020] Governança Quádrupla de Ferramentas e Eliminação de Loops:** Para deter o consumo desproporcional de tokens por chamadas repetitivas e exploração desordenada, o kit aplica 4 defesas simultâneas: (1) Loop Detection no hook `smart_tool_optimizer.py` (hash sha256 de tool+args bloqueando a 3ª repetição idêntica consecutiva com `deny`); (2) Repo Map Atômico em `.agents/memory/REPO_MAP.md` via `agy-repo-map` gerando resumo AST < 80 linhas que zera chamadas cegas de `list_dir` e `grep_search`; (3) Auto-Compaction e descarte de saídas efêmeras de ferramentas aos 15 turnos / 40k tokens; e (4) Zero-Tool Gate para consultas conceituais L0.


---

## 7. Technical Debts & Known Blockers
- **Nenhum bloqueio ativo.** CI/CD Auto-Healer operacional, 29/29 testes unitários aprovados, comandos integrados em `~/.local/bin/`, git hooks ativos e persistência de disco rigorosamente cumprida.




---
## [v2.14.0] - Token Tracker: 5 Bugs de Contabilização Corrigidos

### Bugs Corrigidos em `scripts/token_tracker.py`

| # | Bug | Impacto | Correção |
|---|-----|---------|----------|
| 1 | Rolling window estimava tokens via linha JSONL bruta | Overestimava 3-5x (metadata JSON incluso) | `calculate_rolling_windows()` parseia `content+thinking` de cada step |
| 2 | Steps `is_truncated=True` eram contados no contexto ativo | Double-counting de conteúdo já removido | Loop pula steps com `is_truncated: true` |
| 3 | `CONVERSATION_HISTORY` contava 100% | Double-counting de resumos de histórico | HISTORY conta 50% (compressão); CHECKPOINT e KNOWLEDGE_ARTIFACTS contam 100% |
| 4 | `estimate_tokens(" " * bytes)` usava ratio uniforme | Tool outputs (JSON) subestimados, prose superestimados | `_tokens_from_bytes(bytes, ratio)` com ratios por tipo: PROSE=4.0, CODE=3.2, MIXED=3.5, CONFIG=3.3 |
| 5 | `detect_model_name()` ignorava env vars e config.json | Fallback errado para Gemini ao usar Claude | Pipeline: env vars → config.json → SQLite → padrão |

### Nova função auxiliar
- `_tokens_from_bytes(byte_count, chars_per_token)` — conversão direta sem proxy de espaços
- `_measure_system_prompt_bytes()` — lê tamanho real de regras/schemas no disco

### Lição Procedural
- **[L-018]** Nunca use `estimate_tokens(" " * bytes)` como proxy de byte→token. Esse padrão ignora o ratio de code_chars e sempre usa chars_per_token=3.8 (prose puro), subestimando outputs de ferramentas JSON/código em ~16% e superestimando prose em ~5%.
- **[L-020]** O acúmulo de outputs de ferramentas em conversas longas gera inflação exponencial de tokens faturados a cada novo turno. Mitiga-se na fonte com 4 defesas: (1) teto estrito de 40 linhas em `view_file`, (2) sanitização mandatória via `agy-sanitize`/pipes em `run_command`, (3) auditoria de payload em hook `PostToolUse` (`tool-size-guard.py`) e (4) antecipação do session reset para 15 turnos / 40k tokens.
- **[L-021]** Modulação de Reasoning Effort Inteligente no CLI (`agy-smart` / `agy-effort`): Mudar o effort manualmente a cada comando cria atrito e desperdício de tokens. O roteador inteligente inspeciona o prompt (L0 trivial -> low, L1 -> medium, L2/L3 -> high), inspeciona o contexto git (branches `docs/` ou `feat/`, arquivos `migration` ou `*.md`) e cruza com a telemetria ao vivo: se a cota móvel de 5h ou semanal estiver crítica (>80%), aplica downshift automático (HIGH -> MEDIUM, MEDIUM -> LOW), protegendo a conta contra interrupções abruptas por rate limit.
- **[L-022]** Interceptação do Binário Nativo vs Wrapper e Disambiguação de Keywords em Classificadores de Risco: Quando a CLI Antigravity for invocada via `agy`, o binário original em `~/.local/bin/agy-native` deve ser envelopado por `~/.local/bin/agy` (apontando para `agy-wrapper.sh` -> `agy_effort_router.py`), garantindo que qualquer chamada pelo usuário ou shell alias (`alias agy="agy --mode accept-edits"`) passe pelo roteador. Além disso, argumentos de flags (como `--mode accept-edits`) não devem ser capturados como prompt e a palavra `token` em L3 deve ser restrita a tokens de autenticação (`jwt`, `access token`), impedindo que perguntas sobre tokens LLM sejam promovidas erroneamente para L3 Crítico.

---

## [v2.16.0] - Correção do Roteamento de Reasoning Effort e Interceptação Global do Binário no CLI

### Correções Implementadas
1. **Disambiguação de `\btoken\b`:** Separado em tokens de auth/segurança (`jwt`, `bearer`, `access token`) em L3 e perguntas sobre tokens/consumo LLM mapeadas para L0.
2. **Expansão de `L0_KEYWORDS`:** Adicionados padrões de dúvidas conceituais e perguntas em português (`do que se trata`, `o que faz`, `para que serve`, `duvida`, `economiza`, `qual a diferen[çc]a`, `de forma simples`).
3. **Correção de Argument Parsing:** `parse_cli_session_args()` agora reconhece flags com valor (`--mode accept-edits`, `-m`, etc.), evitando que valores de flags sejam capturados como prompt da tarefa.
4. **Interceptação Global do Binário Nativo:** O binário ELF original foi movido para `~/.local/bin/agy-native` e `~/.local/bin/agy` foi convertido em symlink para `agy-wrapper.sh`. Agora, tanto `agy`, `agy-smart`, `agy-fast` quanto `agy-deep` executam através do classificador inteligente com sincronização imediata de `settings.json`.
5. **Anti-False-Positive em `detect_effort`:** Adicionado filtro contra saídas de ferramentas que contêm código-fonte no transcript, evitando que referências literais a `Model Selection` no código sobrescrevam o esforço real.
6. **Implantação Global Universal:** Executada varredura e sincronização em todos os 53 projetos e workspaces locais (`apply_ignore_rules.py` e `install-global.sh`), propagando `.geminiignore`, `.antigravityignore`, symlinks globais do kit e hooks de push para observabilidade.


